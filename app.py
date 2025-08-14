import streamlit as st
import pandas as pd

st.set_page_config(page_title="Conciliación Bancaria Automatizada", layout="wide")

st.title("📊 Conciliación Bancaria Automatizada")
st.write("Sube los archivos de movimientos del Banco y del ERP para generar la conciliación automática.")

# Subida de archivos
banco_file = st.file_uploader("📁 Cargar archivo del Banco (Excel)", type=["xlsx"])
erp_file = st.file_uploader("📁 Cargar archivo del ERP (Excel)", type=["xlsx"])

if banco_file and erp_file:
    try:
        # Cargar datos
        df_banco = pd.read_excel(banco_file)
        df_erp = pd.read_excel(erp_file)

        # Normalizar columnas
        df_banco.columns = df_banco.columns.str.strip().str.lower()
        df_erp.columns = df_erp.columns.str.strip().str.lower()

        # Validar que contengan columnas necesarias
        required_cols = {"fecha", "monto", "descripcion"}
        if not required_cols.issubset(df_banco.columns) or not required_cols.issubset(df_erp.columns):
            st.error(f"Los archivos deben tener estas columnas: {required_cols}")
        else:
            # Conciliación automática
            conciliados = pd.merge(df_banco, df_erp, on=["fecha", "monto"], how="inner")
            no_banco = df_erp.merge(df_banco, on=["fecha", "monto"], how="left", indicator=True)
            no_banco = no_banco[no_banco["_merge"] == "left_only"]
            no_erp = df_banco.merge(df_erp, on=["fecha", "monto"], how="left", indicator=True)
            no_erp = no_erp[no_erp["_merge"] == "left_only"]

            st.subheader("✅ Movimientos conciliados")
            st.dataframe(conciliados)

            st.subheader("❌ Movimientos en ERP no encontrados en Banco")
            st.dataframe(no_banco)

            st.subheader("❌ Movimientos en Banco no encontrados en ERP")
            st.dataframe(no_erp)

            # Descargar resultados
            output = pd.ExcelWriter("resultado_conciliacion.xlsx", engine="xlsxwriter")
            conciliados.to_excel(output, sheet_name="Conciliados", index=False)
            no_banco.to_excel(output, sheet_name="Solo_ERP", index=False)
            no_erp.to_excel(output, sheet_name="Solo_Banco", index=False)
            output.close()

            with open("resultado_conciliacion.xlsx", "rb") as f:
                st.download_button("📥 Descargar conciliación en Excel", f, "resultado_conciliacion.xlsx")
    except Exception as e:
        st.error(f"Error al procesar los archivos: {e}")