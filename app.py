import streamlit as st
import ai_logic
import solver


def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


st.set_page_config(page_title="Optimalizátor řezných problémů")

try:
    load_css("styles.css")
except FileNotFoundError:
    st.error("Nepodařilo se načíst styles.css")

st.title("Optimalizátor řezných problémů")

with st.sidebar:
    st.header("Nastavení")
    api_key = st.text_input("Vlož Gemini API Key", type="password")
    st.caption("Klíč z aistudio.google.com")

    st.divider()

    st.subheader("Nastavení pily")
    kerf_width = st.number_input("Šířka řezu (mm)", min_value=0, max_value=10, value=3)

    st.divider()
    with st.expander("Debug nástroje"):
        if st.button("Zjistit dostupné modely"):
            if not api_key:
                st.error("Nejdřív vlož klíč!")
            else:
                try:
                    models = ai_logic.list_available_models(api_key)
                    st.write("Dostupné modely:")
                    for m in models:
                        if 'generateContent' in m.supported_generation_methods:
                            st.code(m.name)
                except Exception as e:
                    st.error(f"Chyba: {e}")

# --- MAIN CONTENT ---
text_input = st.text_area("Zadání", height=150,
                          placeholder="Nařež mi 10 jeklů, délka dva metry. Máme skladem 6m i 4m tyče.")

if st.button("Spočítat"):
    if not api_key:
        st.error("Chybí API klíč!")
    else:
        with st.spinner("Přemýšlím..."):
            try:
                # 1. AI
                data = ai_logic.parse_request_with_ai(text_input, api_key)

                # Display Info
                stock_types = ", ".join([f"{d}mm" for d in data.stock_lengths_mm])
                st.success(f"Pochopeno: {data.material_type}")
                st.info(f"Skladem dostupné délky: {stock_types} | Prořez pily: {kerf_width}mm")

                # 2. Solver - sending data FROM AI + kerf FROM UI
                result = solver.calculate_cutting_plan(data, int(kerf_width))

                # 3. Results
                col1, col2 = st.columns(2)
                col1.metric("Použité tyče", f"{len(result.bars)} ks")
                col2.metric("Celkový odpad", f"{result.total_waste_mm} mm")

                st.subheader("Plán řezání:")
                # result.cutting_instructions is a list of tuples (description, percentage)
                for description, percentage in result.cutting_instructions:
                    st.text(description)
                    st.progress(percentage / 100)

            except Exception as e:
                st.error(f"Chyba: {e}")
                st.info("Tip: Zkontroluj název modelu v kódu nebo API klíč.")