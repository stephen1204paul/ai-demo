"""
Script to add Tanglish translations to all dialogue files.

Tanglish = Tamil + English mix (how people actually speak)
"""

import json
from pathlib import Path

# Tanglish translations for Vadivelu
vadivelu_tanglish = {
    "என்ன கொடுமை சார் இது": "Enna koduma sir idhu",
    "என்னடா இந்த ட்ராஃபிக்": "Ennada indha traffic, naan yesterday-la veetla irundhu start panninen, innum stuck-ah irukken!",
    "நான் பேசறதே உங்களுக்கு விளங்கலையா": "Naan pesaradhey ungalukku vizhangalaya?",
    "என் கதை கேட்டால் கதறி அழுவீங்க": "En kadhai kettaa kadhara azhuveenga",
    "பேய் பேய்... பயமா இருக்கு": "Pey pey... bayama irukku!",
    "நான் ராஜா... ஆனா என்னோட சம்பளம் மட்டும் குறைவு": "Naan raja... aana ennoda salary mattum koraiva irukku!",
    "கல்யாணம் பண்ணிக்கணும்னா அதுக்கு முன்னாடி எல்லாரும் யோசிக்கணும்": "Kalyanam pannikanumna adhukku munnaadi yosikanum, kalyanam aacha piragu yosichadhula use illa!",
    "நான் முட்டாள் மாதிரி தெரிஞ்சாலும் புத்திசாலி": "Naan muttaal madhiri therinjaalum, actually naan puddhisaali!",
    "சென்னை ரோட்ல ஒரே ஒரு நாள் ஓட்டுனா போதும், எல்லா பொறுமையும் கத்துக்கலாம்": "Chennai road-la orey oru naal ottuna podhum, ella porumaiyum kathukalam!",
    "நான் வெளிநாட்டுல படிச்சவன்... ஆனா எனக்கு தமிழ் தான் comfortable": "Naan foreign-la padicha aalu... aana enakku Tamil dhan comfortable!",
    "காதல் என்றால் கஷ்டம், அதுவும் என் மாதிரி ஆளுக்கு double கஷ்டம்": "Kaadhal-na kashtam, adhuvum en madhiri aalukku double kashtam!",
    "எனக்கு புரிஞ்சது என்னன்னா... எனக்கு ஒன்னும் புரியல": "Enakku purinjadhu ennana... enakku onnum puriyala!",
    "இந்த phone வாங்கினா உங்க வாழ்க்கையே change ஆயிடும்... அதுவும் worst-கு": "Indha phone vaangina unga life-ey change aayidum... adhuvum worst-ku!",
    "எல்லாம் விதி... ஆனா விதி என்ன செஞ்சாலும் நான் suffering தான்": "Ellam vidhi... aana vidhi enna senjaalum naan suffering dhan!",
    "நான் பாதுகாப்பு தருவேன்... ஆனா என்னையும் யாரவது பாதுகாக்கணும்": "Naan protection tharuven... aana ennaiyum yaaravadhu protect pannanum!",
    "நண்பர்கள் இருந்தாலே போதும், எதிரிகள் தானா வருவாங்க": "Friends irundhaale podhum, enemies thaana varuvaanga!",
    "ஊர்ல சும்மா இருக்கலாம், ஆனா சென்னைல சும்மா இருந்தா வேலை இல்லாதவன் மாதிரி தெரியும்": "Ooru-la summa iruklaam, aana Chennai-la summa irundhaa vela illadhavan madhiri theriyum!",
    "சாப்பாடு இருந்தா எல்லா பிரச்சனைக்கும் solution இருக்கு": "Saapadu irundhaa ella problem-kukkum solution irukku!",
    "என்னோட luck வேற level, எல்லாம் தலைகீழா தான் நடக்கும்": "Ennoda luck vera level, ellam thalai keezha dhan nadakkum!",
    "வேலை செய்யறதுக்கு பதிலா வேலை செய்ற மாதிரி நடிக்கறது easy": "Vela seiyaradhukku badhila vela seiyara madhiri nadikkaradhu easy!",
    "பணம் இல்லாம சந்தோஷமா இருக்கலாம்னு சொல்றாங்க... அது பணம் இருக்கவங்க தான் சொல்றாங்க": "Panam illama sandhoshama iruklaamnu solraanga... adhu panam irukkavanga dhan solraanga!",
    "மீட்டர் வச்சிருக்கோம், ஆனா அது decoration-க்கு தான்": "Meter vechirukkom, aana adhu decoration-ku dhan!",
    "எல்லா உறவும் நல்லா இருக்கு... கடன் கேட்கும் வரைக்கும்": "Ella relationship-um nalla irukku... loan kekkum varaikkum!",
    "நம்பிக்கை தான் business-ல முக்கியம்... அதான் நான் யாரையும் நம்புறதில்லை": "Trust dhan business-la mukkiyam... adhaan naan yaaraiyum namburadhilla!",
    "வாழ்க்கையில கஷ்டம் வந்தா சிரிச்சிட்டே face பண்ணனும்... அழுதா அது மேல tough ஆகும்": "Life-la kashtam vandhaa sirichitte face pannanum... azhudhaa adhu mela tough aagum!",
    "டாக்டர் ஆனா மரியாதை கிடைக்கும்... ஆனா தூக்கம் கிடைக்காது": "Doctor aana respect kidaikkum... aana thookkam kidaikkaadhu!"
}

# Tanglish translations for Santhanam
santhanam_tanglish = {
    "சென்னை ட்ராஃபிக் என்னோட கார்டியோ": "Chennai traffic ennoda cardio, bro!",
    "இதெல்லாம் ரொம்ப over்னு எனக்கே தெரியும்": "Idhellam romba over-nu enakkay theriyum, aana enna pandradhu!",
    "காதல் என்றால் கஷ்டம்தான்": "Kaadhal-na kashtam dhan, adhu universal truth!",
    "Office politics-அ விட குடும்ப politics-அ ஈஸி": "Office politics-a vida kudumba politics easy, atleast unga enemies theriyum!",
    "Style இருந்தா substance இருக்கணும்னு அவசியம் இல்ல": "Style irundhaa substance irukanumnu avasiyam illa, bro!",
    "Facebook-ல எல்லாரும் happy, real life-ல எல்லாரும் tense": "Facebook-la ellarum happy, real life-la ellarum tense!",
    "First date-ல coffee shop போனா safe, restaurant போனா commitment": "First date-la coffee shop ponaa safe, restaurant ponaa commitment, bro!",
    "நண்பன் வீட்ல சாப்பிட்டா அது நட்பு, அவன் பணம் எடுத்தா அது திருட்டு": "Nanbaa veetla saapittaa adhu friendship, avan panam eduththaa adhu theft - thin line, bro!",
    "நல்லா இருக்கறவன் கஷ்டப்படுவான், கெட்டவன் enjoy பண்ணுவான்": "Nallaa irukkaravaan kashtapaduvaaan, kettavan enjoy pannuvaaan - that's the system, bro!",
    "படத்துல logic தேடறவனுக்கு comedy புரியாது": "Padathula logic thedaavanukkku comedy puriyaadhu, bro!",
    "Smartphone வந்த பிறகு people smart ஆகல, phone மட்டும் smart ஆச்சு": "Smartphone vandha piragu people smart aagala, phone mattum smart aachu!",
    "Chennai-ல வாழ்றதுக்கு three முக்கியம்: patience, AC, and more patience": "Chennai-la vaazhradhukku three mukkiyam: patience, AC, and more patience!",
    "Roommate கிட்ட privacy இருக்காது, ஆனா rent share ஆகும்": "Roommate kitta privacy irukkaadhu, aana rent share aagum - tough choice, bro!",
    "பணம் இல்லாதவன் பார்த்தா எல்லாமே expensive": "Panam illadhavan paarthaa ellamey expensive, bro!",
    "எல்லாரும் வெற்றி பெறனும்னு சொல்றாங்க, ஆனா competition-ல நான் மட்டும் ஜெயிக்கணும்": "Ellarum success peranumnu solraanga, aana competition-la naan mattum win aaganum!",
    "Trip plan பண்ணும் போது எல்லாமே நல்லா இருக்கும், போன பிறகு தான் reality": "Trip plan pannum podhu ellamey nalla irukkum, pona piragu dhan reality!",
    "பேரு வச்சிருக்காங்க Rocket, ஆனா speed இல்ல": "Peru vechirukkaanga Rocket, aana speed illa - irony at its peak!",
    "படிச்சா job கிடைக்கும்னு சொன்னாங்க, இப்ப degree வச்சிட்டு taxi ஓட்டுறேன்": "Padicha job kidaikkumnu sonnaanga, ippo degree vechiittu taxi ottureen!",
    "Hero வாறதுக்கு முன்னாடி நானும் ஓடலாம், ஆனா scene வேணுமே": "Hero varadhukku munnaadi naanum odalaam, aana scene venumeybro!",
    "சமையல் பண்ண தெரியாதவன் marriage பண்ணிக்கணும்": "Samayal panna theriyaadhavan marriage pannikanum - simple solution, bro!",
    "Gym போறவன் photo போடுவான், workout பண்ணலைனாலும் paravala": "Gym poravan photo poduvaanbworkout pannalainaalum paravala - it's all about the flex!",
    "ஊர்ல respect, சென்னைல competition": "Ooru-la respect, Chennai-la competition!",
    "Online shopping-ல photo வேற மாதிரி, delivery வேற மாதிரி": "Online shopping-la photo vera madhiri, delivery vera madhiri!",
    "Customer எப்பவும் right-னு சொல்றாங்க, ஆனா customer எப்பவும் confusing": "Customer eppavum right-nu solraanga, aana customer eppavum confusing!",
}

# Tanglish translations for Vivek
vivek_tanglish = {
    "நம்ம எஜுகேஷன் சிஸ்டம் memory test, not knowledge test": "Namma education system memory test, not knowledge test!",
    "சின்ன சின்ன முறைகேடுகள் சேர்ந்துதான் பெரிய ஊழல்": "Chinna chinna irregularities serndhudhan periya corruption!",
    "நாம tradition-அ மறக்காம technology-அ கத்துக்கணும்": "Naama tradition-a marakkama technology-a kathukanum!",
    "English-ல என்ன சொன்னாலும் தமிழ்ல translate பண்ணா comedy-தான்": "English-la enna sonnaalum Tamil-la translate pannaa comedy dhan!",
    "மரம் வளர்ப்போம், பூமி காப்போம்": "Maram valarpom, boomi kaappom - even comedy can have a message!",
    "அரசியல்வாதிகள் வாக்குறுதி தருவாங்க, ஆனா யாரும் வார்த்தை காப்பாங்கன்னு guarantee இல்ல": "Politicians vaakkurudhi tharuvaanga, aana yaarum varthai kaappaanganu guarantee illa!",
    "அழகு முகத்துல இல்லை, மனசுல இருக்கு... ஆனா photo முகம் தான் வரும்": "Azhagu mugatthula illa, manasula irukku... aana photo-la mukam dhan varum!",
    "Technology வளர்ந்திருக்கு, ஆனா மனித நேயம் குறைஞ்சிருக்கு": "Technology valarndhirukku, aana humanity korainjirukku!",
    "Hero-வ கடவுள் மாதிரி வணங்கறோம், ஆனா நல்ல மனிதனை மதிக்கறதில்லை": "Hero-va kadavul madhiri vanangrom, aana nalla manidhanai mathikkaradhilla!",
    "சட்டம் எல்லாருக்கும் சமம்னு சொல்றாங்க... ஆனா பணக்காரனுக்கு வேற, ஏழைக்கு வேற": "Law ellarukkum samam-nu solraanga... aana rich-ukku vera, poor-ukku vera!",
    "MBA படிச்சா job கிடைக்கும்னு நினைச்சேன், இப்ப tea கடைல MBA வேஸ்ட்னு சொல்றாங்க": "MBA padicha job kidaikumnu ninaichen, ippo tea kadai-la MBA waste-nu solraanga!",
    "காதல் பணத்துக்காக இல்லன்னு சொல்றாங்க, ஆனா பணம் இல்லாம காதல் நடக்காது": "Kaadhal panathukkaga illanu solraanga, aana panam illama kaadhal nadakkaadhu!",
    "ஜிம் போய் உடம்பை வளர்க்கறோம், ஆனா மனசை வளர்க்க நேரம் இல்ல": "Gym poi udambai valarkkrom, aana manasai valarkka time illa!",
    "படத்துல பாக்கறதெல்லாம் real இல்ல, ஆனா படம் பார்த்து real-ல follow பண்றோம்": "Padathula paakkradhellam real illa, aana padam paathu real-la follow panrom!",
    "தாய் அன்பு கடல் மாதிரி, அளக்க முடியாது... but பசங்க realize பண்றதுக்கு ரொம்ப நாள் ஆகும்": "Thaai anbu kadal madhiri, alaka mudiyaadhu... but pasanga realize panradhukku romba naal aagum!",
    "English பேசினா smart-னு நினைக்கறோம், தமிழ் பேசினா backward-னு நினைக்கறோம் - இது தான் நம்ம problem": "English pesinaa smart-nu ninaikkrom, Tamil pesinaa backward-nu ninaikkrom - idhu dhan namma problem!",
    "உண்மை பேசினா மரியாதை இல்ல, பொய் சொன்னா politician ஆகலாம்": "Unmai pesinaa respect illa, poi sonnaa politician aagalaam!",
    "நம்ம காலத்துல respect முக்கியம், இன்னைக்கு freedom முக்கியம்": "Namma kaalaththula respect mukkiyam, innaiku freedom mukkiyam!",
    "கல்யாணத்துக்கு முன்னாடி ஜாதகம் பார்ப்பாங்க, கல்யாணம் ஆன பிறகு adjustment தான் முக்கியம்": "Kalyanathukku munnaadi jadhagam paarpanga, kalyanam aana piragu adjustment dhan mukkiyam!",
    "Police வேல சிரமமானது... public எப்பவும் complain பண்ணும், ஆனா cooperation பண்ண மாட்டாங்க": "Police vela siramamaanadhu... public eppavum complain pannum, aana cooperation panna maattaanga!",
    "Youth power பெருசு, ஆனா responsibility-ல youth interest இல்ல": "Youth power perusu, aana responsibility-la youth interest illa!",
    "ஜாதி பார்க்கறதுல நம்ம expert, ஆனா மனிதத்தை பார்க்க மறந்துட்டோம்": "Jaadhi paakkradhu-la namma expert, aana humanity paakka marandhuttom!",
    "Science படிக்கறோம், ஆனா superstition-ஐ follow பண்றோம்": "Science padikkrom, aana superstition-ai follow panrom!",
    "Global warming பத்தி எல்லாரும் பேசறாங்க, ஆனா யாரும் மாத்த ready இல்ல": "Global warming pathi ellarum pesraanga, aana yaarum maatha ready illa!"
}

def add_tanglish_to_file(filename, tanglish_dict):
    """Add Tanglish translations to dialogue file."""
    filepath = Path(__file__).parent.parent / 'data' / 'raw' / filename

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Add tanglish field to each dialogue
    for dialogue in data['dialogues']:
        tamil_text = dialogue['dialogue_tamil']

        # Get tanglish from dictionary
        if tamil_text in tanglish_dict:
            dialogue['dialogue_tanglish'] = tanglish_dict[tamil_text]
        else:
            # Fallback: use English as tanglish if not in dict
            dialogue['dialogue_tanglish'] = dialogue['dialogue_english']

    # Write back with proper formatting
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Added Tanglish to {filename}")
    print(f"   Total dialogues: {len(data['dialogues'])}")

if __name__ == '__main__':
    print("Adding Tanglish translations to all dialogue files...\n")

    add_tanglish_to_file('vadivelu_dialogues.json', vadivelu_tanglish)
    add_tanglish_to_file('santhanam_dialogues.json', santhanam_tanglish)
    add_tanglish_to_file('vivek_dialogues.json', vivek_tanglish)

    print("\n🎉 All files updated with Tanglish translations!")
    print("\nNext steps:")
    print("1. Check the JSON files to verify formatting")
    print("2. Run: python scripts/populate_data.py")
    print("3. Run: python scripts/generate_embeddings.py")
