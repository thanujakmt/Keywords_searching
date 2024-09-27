
host = "helenzys-mysql-dev.clyhoefsujtn.us-east-1.rds.amazonaws.com"

niche = "holistic_health"

destination_table_name = f"{niche}_websites"

source_user = 'gmb_admin'
source_password = 'icyF%40ng36'

if niche == "acupuncturists":
    source_database = "usa_acupuncturists_db"
elif niche == "yoga_studio":
    source_database = "usa_yoga_db"
else:
    source_database = f"{niche}_business_db"

target_user = 'htb_websites_db'
target_password = 'gol)Force72'
target_database = 'htb_websites_db'

countries = ['usa','au','ca','se','uk','dk','nz','uae']

niche = 'acupuncturists'

niche_list = [
    # 'osteopath',
    'holistic_health',
    'naprapath',
    'herbalist',
    'dietitian',
    'occupational_therapist',
    'holistic_medicine',
    'wellness_clinics',
    'integrative_medicine',
    'homeopathy',
    'aromatherapy',
    'cranial_sacral_therapy',
    'sound_healing',
    'reflexology',
    'Hypnotherapy',
    'sound_therapy',
    'reiki_healers',
    'herbal_medicine',
    'functional_medicine',
    'energy_healer',
    'ayurveda',
    'acupuncturists',
    'chiropractor',
    'physiotherapist',
    'yoga_studio',
    'massage_therapist',
    'naturopathic_practitioner',
    'nutritionist',
    'meditation'
]
