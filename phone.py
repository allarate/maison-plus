import re
import streamlit as st
import phonenumbers

# (nom, code ISO2, indicatif E.164) — Tchad en premier (indicatif par défaut)
COUNTRY_CODES = [
    ("Tchad", "TD", "+235"),
    ("Afghanistan", "AF", "+93"), ("Afrique du Sud", "ZA", "+27"), ("Albanie", "AL", "+355"),
    ("Algérie", "DZ", "+213"), ("Allemagne", "DE", "+49"), ("Andorre", "AD", "+376"),
    ("Angola", "AO", "+244"), ("Arabie Saoudite", "SA", "+966"), ("Argentine", "AR", "+54"),
    ("Arménie", "AM", "+374"), ("Australie", "AU", "+61"), ("Autriche", "AT", "+43"),
    ("Azerbaïdjan", "AZ", "+994"), ("Bahamas", "BS", "+1242"), ("Bahreïn", "BH", "+973"),
    ("Bangladesh", "BD", "+880"), ("Barbade", "BB", "+1246"), ("Belgique", "BE", "+32"),
    ("Belize", "BZ", "+501"), ("Bénin", "BJ", "+229"), ("Bhoutan", "BT", "+975"),
    ("Biélorussie", "BY", "+375"), ("Birmanie", "MM", "+95"), ("Bolivie", "BO", "+591"),
    ("Bosnie-Herzégovine", "BA", "+387"), ("Botswana", "BW", "+267"), ("Brésil", "BR", "+55"),
    ("Brunei", "BN", "+673"), ("Bulgarie", "BG", "+359"), ("Burkina Faso", "BF", "+226"),
    ("Burundi", "BI", "+257"), ("Cambodge", "KH", "+855"), ("Cameroun", "CM", "+237"),
    ("Canada", "CA", "+1"), ("Cap-Vert", "CV", "+238"), ("Centrafrique", "CF", "+236"),
    ("Chili", "CL", "+56"), ("Chine", "CN", "+86"), ("Chypre", "CY", "+357"),
    ("Colombie", "CO", "+57"), ("Comores", "KM", "+269"), ("Congo-Brazzaville", "CG", "+242"),
    ("Congo-Kinshasa (RDC)", "CD", "+243"), ("Corée du Nord", "KP", "+850"), ("Corée du Sud", "KR", "+82"),
    ("Costa Rica", "CR", "+506"), ("Côte d'Ivoire", "CI", "+225"), ("Croatie", "HR", "+385"),
    ("Cuba", "CU", "+53"), ("Danemark", "DK", "+45"), ("Djibouti", "DJ", "+253"),
    ("Égypte", "EG", "+20"), ("Émirats Arabes Unis", "AE", "+971"), ("Équateur", "EC", "+593"),
    ("Érythrée", "ER", "+291"), ("Espagne", "ES", "+34"), ("Estonie", "EE", "+372"),
    ("Eswatini", "SZ", "+268"), ("États-Unis", "US", "+1"), ("Éthiopie", "ET", "+251"),
    ("Fidji", "FJ", "+679"), ("Finlande", "FI", "+358"), ("France", "FR", "+33"),
    ("Gabon", "GA", "+241"), ("Gambie", "GM", "+220"), ("Géorgie", "GE", "+995"),
    ("Ghana", "GH", "+233"), ("Grèce", "GR", "+30"), ("Grenade", "GD", "+1473"),
    ("Guatemala", "GT", "+502"), ("Guinée", "GN", "+224"), ("Guinée-Bissau", "GW", "+245"),
    ("Guinée Équatoriale", "GQ", "+240"), ("Guyana", "GY", "+592"), ("Haïti", "HT", "+509"),
    ("Honduras", "HN", "+504"), ("Hongrie", "HU", "+36"), ("Inde", "IN", "+91"),
    ("Indonésie", "ID", "+62"), ("Irak", "IQ", "+964"), ("Iran", "IR", "+98"),
    ("Irlande", "IE", "+353"), ("Islande", "IS", "+354"), ("Israël", "IL", "+972"),
    ("Italie", "IT", "+39"), ("Jamaïque", "JM", "+1876"), ("Japon", "JP", "+81"),
    ("Jordanie", "JO", "+962"), ("Kazakhstan", "KZ", "+7"), ("Kenya", "KE", "+254"),
    ("Kirghizistan", "KG", "+996"), ("Kiribati", "KI", "+686"), ("Kosovo", "XK", "+383"),
    ("Koweït", "KW", "+965"), ("Laos", "LA", "+856"), ("Lesotho", "LS", "+266"),
    ("Lettonie", "LV", "+371"), ("Liban", "LB", "+961"), ("Liberia", "LR", "+231"),
    ("Libye", "LY", "+218"), ("Liechtenstein", "LI", "+423"), ("Lituanie", "LT", "+370"),
    ("Luxembourg", "LU", "+352"), ("Macédoine du Nord", "MK", "+389"), ("Madagascar", "MG", "+261"),
    ("Malaisie", "MY", "+60"), ("Malawi", "MW", "+265"), ("Maldives", "MV", "+960"),
    ("Mali", "ML", "+223"), ("Malte", "MT", "+356"), ("Maroc", "MA", "+212"),
    ("Maurice", "MU", "+230"), ("Mauritanie", "MR", "+222"), ("Mexique", "MX", "+52"),
    ("Micronésie", "FM", "+691"), ("Moldavie", "MD", "+373"), ("Monaco", "MC", "+377"),
    ("Mongolie", "MN", "+976"), ("Monténégro", "ME", "+382"), ("Mozambique", "MZ", "+258"),
    ("Namibie", "NA", "+264"), ("Nauru", "NR", "+674"), ("Népal", "NP", "+977"),
    ("Nicaragua", "NI", "+505"), ("Niger", "NE", "+227"), ("Nigeria", "NG", "+234"),
    ("Norvège", "NO", "+47"), ("Nouvelle-Zélande", "NZ", "+64"), ("Oman", "OM", "+968"),
    ("Ouganda", "UG", "+256"), ("Ouzbékistan", "UZ", "+998"), ("Pakistan", "PK", "+92"),
    ("Palaos", "PW", "+680"), ("Palestine", "PS", "+970"), ("Panama", "PA", "+507"),
    ("Papouasie-Nouvelle-Guinée", "PG", "+675"), ("Paraguay", "PY", "+595"), ("Pays-Bas", "NL", "+31"),
    ("Pérou", "PE", "+51"), ("Philippines", "PH", "+63"), ("Pologne", "PL", "+48"),
    ("Portugal", "PT", "+351"), ("Qatar", "QA", "+974"), ("République Dominicaine", "DO", "+1809"),
    ("République Tchèque", "CZ", "+420"), ("Roumanie", "RO", "+40"), ("Royaume-Uni", "GB", "+44"),
    ("Russie", "RU", "+7"), ("Rwanda", "RW", "+250"), ("Saint-Marin", "SM", "+378"),
    ("Sainte-Lucie", "LC", "+1758"), ("Salvador", "SV", "+503"), ("Samoa", "WS", "+685"),
    ("São Tomé-et-Principe", "ST", "+239"), ("Sénégal", "SN", "+221"), ("Serbie", "RS", "+381"),
    ("Seychelles", "SC", "+248"), ("Sierra Leone", "SL", "+232"), ("Singapour", "SG", "+65"),
    ("Slovaquie", "SK", "+421"), ("Slovénie", "SI", "+386"), ("Somalie", "SO", "+252"),
    ("Soudan", "SD", "+249"), ("Soudan du Sud", "SS", "+211"), ("Sri Lanka", "LK", "+94"),
    ("Suède", "SE", "+46"), ("Suisse", "CH", "+41"), ("Suriname", "SR", "+597"),
    ("Syrie", "SY", "+963"), ("Tadjikistan", "TJ", "+992"), ("Tanzanie", "TZ", "+255"),
    ("Thaïlande", "TH", "+66"), ("Timor Oriental", "TL", "+670"),
    ("Togo", "TG", "+228"), ("Tonga", "TO", "+676"), ("Trinité-et-Tobago", "TT", "+1868"),
    ("Tunisie", "TN", "+216"), ("Turkménistan", "TM", "+993"), ("Turquie", "TR", "+90"),
    ("Tuvalu", "TV", "+688"), ("Ukraine", "UA", "+380"), ("Uruguay", "UY", "+598"),
    ("Vanuatu", "VU", "+678"), ("Vatican", "VA", "+379"), ("Venezuela", "VE", "+58"),
    ("Vietnam", "VN", "+84"), ("Yémen", "YE", "+967"), ("Zambie", "ZM", "+260"),
    ("Zimbabwe", "ZW", "+263"),
]

def _flag(iso2):
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in iso2.upper())


def phone_input(key_prefix, label="Téléphone"):
    """Renders a single visual "Téléphone" field: an indicatif dropdown fused
    to a number input, styled with no gap/border between them so it reads as
    one control. Returns the combined number (e.g. "+235612345678") or None
    if the number part is empty.
    """
    marker = f"phone-{key_prefix}"
    st.markdown(
        f'<div id="{marker}">'
        f'<style>'
        f'div[data-testid="stElementContainer"]:has(#{marker})'
        f' + div [data-testid="stHorizontalBlock"] {{'
        f'   gap: 0 !important; align-items: stretch;'
        f' }}'
        f'div[data-testid="stElementContainer"]:has(#{marker})'
        f' + div [data-testid="stHorizontalBlock"] [data-baseweb="select"] > div {{'
        f'   border-top-right-radius: 0 !important;'
        f'   border-bottom-right-radius: 0 !important;'
        f'   border-right: none !important;'
        f' }}'
        f'div[data-testid="stElementContainer"]:has(#{marker})'
        f' + div [data-testid="stHorizontalBlock"] [data-testid="stTextInput"] input {{'
        f'   border-top-left-radius: 0 !important;'
        f'   border-bottom-left-radius: 0 !important;'
        f' }}'
        f'</style>'
        f'<p>{label}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    col_code, col_num = st.columns([1, 4], gap="small")
    with col_code:
        choice = st.selectbox(
            "Indicatif", COUNTRY_CODES, index=0,
            format_func=lambda c: f"{_flag(c[1])} {c[2]}",
            key=f"{key_prefix}_indicatif", label_visibility="collapsed",
        )
    with col_num:
        local_number = st.text_input(
            "Numéro", key=f"{key_prefix}_numero",
            placeholder="6XX XXX XXX", label_visibility="collapsed",
        )

    digits = re.sub(r"\D", "", local_number)
    if not digits:
        return None
    return choice[2] + digits


def is_valid_phone(number):
    """Format validity per the country embedded in the indicatif (via phonenumbers)."""
    if not number:
        return False
    try:
        parsed = phonenumbers.parse(number, None)
    except phonenumbers.NumberParseException:
        return False
    return phonenumbers.is_valid_number(parsed)
