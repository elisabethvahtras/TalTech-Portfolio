import os

import pandas as pd
import streamlit as st


# Muudab sekundid kujule minutid:sekundid.sajandikud
def vorminda_aeg(aeg):
    kokku = round(float(aeg) * 100)
    minutid = kokku // 6000
    sekundid = (kokku % 6000) // 100
    sajandikud = kokku % 100
    return f"{minutid:02d}:{sekundid:02d}.{sajandikud:02d}"


DISTANTSID = ["50 m", "100 m", "200 m", "400 m", "800 m", "1500 m"]

st.title("🏊 SportProgress")
st.write("Sporditulemuste analüüsi äpp")

# Laeme tulemused ja eesmärgid ainult seansi alguses
if "tulemused" not in st.session_state:
    if os.path.exists("tulemused.csv"):
        laaditud = pd.read_csv("tulemused.csv")
        laaditud["Kuupäev"] = pd.to_datetime(laaditud["Kuupäev"]).dt.date
        st.session_state.tulemused = laaditud.values.tolist()
    else:
        st.session_state.tulemused = []

if "eesmargid" not in st.session_state:
    if os.path.exists("eesmargid.csv"):
        laaditud = pd.read_csv("eesmargid.csv")
        st.session_state.eesmargid = laaditud.values.tolist()
    else:
        st.session_state.eesmargid = []

# Ühine tabel kõigile vahelehtedele
tabel = pd.DataFrame(
    st.session_state.tulemused,
    columns=["Sportlane", "Distants", "Aeg (s)", "Kuupäev"]
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Tulemused", "📈 Analüüs", "🎯 Eesmärgid", "🏆 Medalid", "👤 Profiil"
])


# 1. TULEMUSED
with tab1:
    st.subheader("Lisa uus tulemus")

    nimi = st.text_input("Sportlase nimi")
    distants = st.selectbox("Vali distants", DISTANTSID)
    minutid = st.number_input("Minutid", min_value=0, step=1)
    sekundid = st.number_input("Sekundid", min_value=0, max_value=59, step=1)
    sajandikud = st.number_input("Sajandikud", min_value=0, max_value=99, step=1)
    kuupaev = st.date_input("Tulemuse kuupäev")

    # Arvutamiseks hoiame aega sekundites
    aeg = round(minutid * 60 + sekundid + sajandikud / 100, 2)

    if st.button("Lisa tulemus"):
        nimi = nimi.strip()

        if nimi and aeg > 0:
            varasemad = []
            for tulemus in st.session_state.tulemused:
                if tulemus[0] == nimi and tulemus[1] == distants:
                    varasemad.append(float(tulemus[2]))

            if not varasemad:
                st.success("🌟 Esimene samm on tehtud! Siit algab sinu areng!")
            elif aeg < min(varasemad):
                eelmine_rekord = min(varasemad)
                paranemine = eelmine_rekord - aeg
                st.balloons()
                st.success("🏆 WOW! UUS ISIKLIK REKORD!")
                st.metric("Eelmine rekord", vorminda_aeg(eelmine_rekord))
                st.metric("Uus rekord", vorminda_aeg(aeg))
                st.success(f"🎉 Parandasid rekordit {paranemine:.2f} sekundi võrra!")
            elif aeg > varasemad[-1]:
                st.info("💪 Ära anna alla! Iga treening viib sind eesmärgile lähemale!")
            else:
                st.success("👏 Tubli töö! Jätka samas vaimus!")

            st.session_state.tulemused.append([nimi, distants, aeg, kuupaev])
            tabel = pd.DataFrame(
                st.session_state.tulemused,
                columns=["Sportlane", "Distants", "Aeg (s)", "Kuupäev"]
            )
            tabel.to_csv("tulemused.csv", index=False)
        else:
            st.error("Sisesta sportlase nimi ja korrektne tulemus!")

    st.subheader("📋 Minu tulemused")
    if not tabel.empty:
        kuvatav_tabel = tabel.copy()
        kuvatav_tabel["Tulemus"] = kuvatav_tabel["Aeg (s)"].apply(vorminda_aeg)
        kuvatav_tabel = kuvatav_tabel.drop(columns=["Aeg (s)"])
        st.dataframe(kuvatav_tabel, hide_index=True)
    else:
        st.info("Tulemusi pole veel lisatud.")


# 2. ANALÜÜS
with tab2:
    st.subheader("🏆 Isiklik rekord")

    if not tabel.empty:
        sportlane = st.selectbox("Vali sportlane rekordi vaatamiseks", tabel["Sportlane"].unique())
        sportlase_andmed = tabel[tabel["Sportlane"] == sportlane]
        rekordi_distants = st.selectbox(
            "Vali distants rekordi vaatamiseks", sportlase_andmed["Distants"].unique()
        )
        andmed = sportlase_andmed[sportlase_andmed["Distants"] == rekordi_distants]
        rekord = andmed["Aeg (s)"].min()
        st.metric("Isiklik rekord", vorminda_aeg(rekord))

        st.subheader("📈 Tulemuste arengugraafik")
        valitud_sportlane = st.selectbox("Vali sportlane graafiku jaoks", tabel["Sportlane"].unique())
        sportlase_andmed = tabel[tabel["Sportlane"] == valitud_sportlane]
        valitud_distants = st.selectbox(
            "Vali distants graafiku jaoks", sportlase_andmed["Distants"].unique()
        )
        andmed = sportlase_andmed[
            sportlase_andmed["Distants"] == valitud_distants
        ].copy()
        andmed["Kuupäev"] = pd.to_datetime(andmed["Kuupäev"])
        andmed = andmed.sort_values("Kuupäev")
        st.line_chart(andmed, x="Kuupäev", y="Aeg (s)")
        st.caption("Graafikul on aeg sekundites. Mida madalam joon, seda parem tulemus.")
    else:
        st.info("Lisa kõigepealt tulemus, et näha analüüsi.")


# 3. EESMÄRGID
with tab3:
    st.subheader("🎯 Minu eesmärgid")

    eesmargi_nimi = st.text_input("Sportlase nimi eesmärgi jaoks")
    eesmargi_distants = st.selectbox("Eesmärgi distants", DISTANTSID)
    eesmargi_minutid = st.number_input("Eesmärgi minutid", min_value=0, step=1)
    eesmargi_sekundid = st.number_input("Eesmärgi sekundid", min_value=0, max_value=59, step=1)
    eesmargi_sajandikud = st.number_input("Eesmärgi sajandikud", min_value=0, max_value=99, step=1)
    eesmargi_aeg = round(
        eesmargi_minutid * 60 + eesmargi_sekundid + eesmargi_sajandikud / 100, 2
    )

    if st.button("Salvesta eesmärk"):
        if eesmargi_nimi.strip() and eesmargi_aeg > 0:
            eesmark = [eesmargi_nimi.strip(), eesmargi_distants, eesmargi_aeg]
            st.session_state.eesmargid.append(eesmark)
            pd.DataFrame(
                st.session_state.eesmargid,
                columns=["Sportlane", "Distants", "Eesmärk (s)"]
            ).to_csv("eesmargid.csv", index=False)
            st.success("🎯 Eesmärk salvestatud!")
        else:
            st.error("Sisesta nimi ja eesmärgi aeg!")

    st.subheader("Eesmärkide täitmine")
    if not st.session_state.eesmargid:
        st.info("Eesmärke pole veel lisatud.")

    for eesmark in st.session_state.eesmargid:
        sportlase_nimi, distants, soovitud_aeg = eesmark
        parim_aeg = None

        # Leiame sportlase parima aja sellel distantsil
        for tulemus in st.session_state.tulemused:
            if tulemus[0] == sportlase_nimi and tulemus[1] == distants:
                if parim_aeg is None or tulemus[2] < parim_aeg:
                    parim_aeg = tulemus[2]

        st.write("**Sportlane:**", sportlase_nimi)
        st.write("**Distants:**", distants)
        st.write("**Eesmärk:**", vorminda_aeg(soovitud_aeg))

        if parim_aeg is None:
            st.info("Lisa esimene tulemus, et eesmärki jälgida!")
        elif parim_aeg <= soovitud_aeg:
            st.success("🏆 EESMÄRK SAAVUTATUD! Suurepärane töö!")
        else:
            puudu = parim_aeg - soovitud_aeg
            st.info(f"💪 Eesmärgini on jäänud {puudu:.2f} sekundit!")
        st.divider()


# 4. MEDALID
with tab4:
    st.subheader("🏅 Minu saavutused")
    medali_nimi = st.text_input("Sportlase nimi medalite vaatamiseks").strip()
    tulemuste_arv = 0

    for tulemus in st.session_state.tulemused:
        if tulemus[0] == medali_nimi:
            tulemuste_arv += 1

    if medali_nimi:
        if tulemuste_arv >= 1:
            st.success("🥉 Esimene samm – sinu esimene tulemus!")
        if tulemuste_arv >= 5:
            st.success("🥈 Sihikindel – oled sisestanud 5 tulemust!")
        if tulemuste_arv >= 10:
            st.success("🥇 Tõeline tegija – oled sisestanud 10 tulemust!")
        if tulemuste_arv == 0:
            st.info("Lisa oma esimene tulemus ja teeni medal!")


# 5. PROFIIL
with tab5:
    st.subheader("👤 Sportlase profiil")
    profiili_nimi = st.text_input("Sportlase nimi profiili vaatamiseks").strip()
    profiili_tulemused = []

    for tulemus in st.session_state.tulemused:
        if tulemus[0] == profiili_nimi:
            profiili_tulemused.append(tulemus)

    if profiili_nimi:
        st.write("Sportlane:", profiili_nimi)
        st.write("Tulemusi kokku:", len(profiili_tulemused))
        rekordid = {}

        # Leiame iga distantsi parima tulemuse
        for tulemus in profiili_tulemused:
            distants = tulemus[1]
            aeg = tulemus[2]
            if distants not in rekordid or aeg < rekordid[distants]:
                rekordid[distants] = aeg

        st.write("Isiklikud rekordid:")
        if rekordid:
            for distants, aeg in rekordid.items():
                st.write(distants, "–", vorminda_aeg(aeg))
        else:
            st.info("Sellel sportlasel pole veel tulemusi.")
