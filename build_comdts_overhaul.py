import os
import sys
import re
import json
import asyncio
from bs4 import BeautifulSoup
import edge_tts
from gtts import gTTS

sys.stdout.reconfigure(encoding='utf-8')

# Dataset for all 32 Commandants
COMDTS_DATA = [
    {
        "art_num": 40,
        "title_en": "Lieutenant Colonel MM Badshah",
        "title_hi": "लेफ्टिनेंट कर्नल एमएम बादशाह",
        "title_pa": "ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਐਮਐਮ ਬਾਦਸ਼ਾਹ",
        "year_en": "October 1947 - August 1948",
        "year_hi": "अक्टूबर 1947 - अगस्त 1948",
        "year_pa": "ਅਕਤੂਬਰ 1947 - ਅਗਸਤ 1948",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "LIEUTENANT COLONEL MM BADSHAH (October 1947 - August 1948)",
        "header_hi": "लेफ्टिनेंट कर्नल एमएम बादशाह (अक्टूबर 1947 - अगस्त 1948)",
        "header_pa": "ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਐਮਐਮ ਬਾਦਸ਼ਾਹ (ਅਕਤੂਬਰ 1947 - ਅਗਸਤ 1948)",
        "writeup_en": "Lieutenant Colonel Man Mohan Badshah was commissioned on 01 February 1938 into 2 SIKH and commanded 2 SIKH during 1947. He became the first Indian Commandant of the Sikh Regimental Centre. Taking command in October 1947 in the turbulent aftermath of Partition, he was responsible for successfully relocating and establishing the Regimental Centre at Ambala. He formulated and formalised standard operating procedures for the Centre and conceived and raised the renowned Regimental Hockey Team at Ambala.",
        "writeup_hi": "लेफ्टिनेंट कर्नल मन मोहन बादशाह 1 फरवरी 1938 को 2 सिख में कमीशन हुए थे और उन्होंने 1947 में 2 सिख की कमान संभाली। वह सिख रेजिमेंटल सेंटर के पहले भारतीय कमांडेंट बने। विभाजन के कठिन समय के दौरान अक्टूबर 1947 में कमान संभालते हुए, उन्होंने रेजिमेंटल सेंटर को अंबाला में सफलतापूर्वक स्थापित और पुनर्गठित किया। उन्होंने सेंटर की मानक संचालन प्रक्रियाओं को औपचारिक रूप दिया तथा अंबाला में प्रसिद्ध रेजिमेंटल हॉकी टीम की स्थापना की।",
        "writeup_pa": "ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਮਨ ਮੋਹਨ ਬਾਦਸ਼ਾਹ 1 ਫਰਵਰੀ 1938 ਨੂੰ 2 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਸਨ ਅਤੇ ਉਨ੍ਹਾਂ ਨੇ 1947 ਵਿੱਚ 2 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਸੰਭਾਲੀ। ਉਹ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੇ ਪਹਿਲੇ ਭਾਰਤੀ ਕਮਾਂਡੈਂਟ ਬਣੇ। ਵੰਡ ਦੇ ਮੁਸ਼ਕਲ ਸਮੇਂ ਦੌਰਾਨ ਅਕਤੂਬਰ 1947 ਵਿੱਚ ਕਮਾਂਡ ਸੰਭਾਲਦਿਆਂ, ਉਨ੍ਹਾਂ ਨੇ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਨੂੰ ਅੰਬਾਲਾ ਵਿੱਚ ਸਫਲਤਾਪੂਰਵਕ ਸਥਾਪਿਤ ਅਤੇ ਪੁਨਰਗਠਿਤ ਕੀਤਾ। ਉਨ੍ਹਾਂ ਨੇ ਸੈਂਟਰ ਦੀਆਂ ਮਿਆਰੀ ਕਾਰਜ ਪ੍ਰਣਾਲੀਆਂ ਨੂੰ ਰਸਮੀ ਰੂਪ ਦਿੱਤਾ ਅਤੇ ਅੰਬਾਲਾ ਵਿਖੇ ਪ੍ਰਸਿੱਧ ਰੈਜੀਮੈਂਟਲ ਹਾਕੀ ਟੀਮ ਦੀ ਸਥਾਪਨਾ ਕੀਤੀ।"
    },
    {
        "art_num": 41,
        "title_en": "Lieutenant Colonel JC Kapoor",
        "title_hi": "लेफ्टिनेंट कर्नल जेसी कपूर",
        "title_pa": "ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਜੇਸੀ ਕਪੂਰ",
        "year_en": "August 1948 - January 1950",
        "year_hi": "अगस्त 1948 - जनवरी 1950",
        "year_pa": "ਅਗਸਤ 1948 - ਜਨਵਰੀ 1950",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "LIEUTENANT COLONEL JC KAPOOR (August 1948 - January 1950)",
        "header_hi": "लेफ्टिनेंट कर्नल जेसी कपूर (अगस्त 1948 - जनवरी 1950)",
        "header_pa": "ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਜੇਸੀ ਕਪੂਰ (ਅਗਸਤ 1948 - ਜਨਵਰੀ 1950)",
        "writeup_en": "Lieutenant Colonel JC Kapoor took over command as the second Indian Commandant of the Sikh Regimental Centre in August 1948, succeeding Lieutenant Colonel MM Badshah. During his tenure until January 1950, he consolidated the training infrastructure and administrative foundation of the Regimental Centre during the post-Independence reorganisation of the Indian Army. He oversaw recruit training, regimental traditions, and welfare initiatives during the critical initial years of the Regiment's modern era.",
        "writeup_hi": "लेफ्टिनेंट कर्नल जेसी कपूर ने अगस्त 1948 में लेफ्टिनेंट कर्नल एमएम बादशाह के बाद सिख रेजिमेंटल सेंटर के दूसरे भारतीय कमांडेंट के रूप में कमान संभाली। जनवरी 1950 तक अपने कार्यकाल के दौरान, उन्होंने स्वतंत्रता के बाद भारतीय सेना के पुनर्गठन के समय रेजिमेंटल सेंटर के प्रशिक्षण बुनियादी ढांचे और प्रशासनिक आधार को सुदृढ़ किया। उन्होंने रेजिमेंट के आधुनिक युग के शुरुआती महत्वपूर्ण वर्षों में रंगरूट प्रशिक्षण, रेजिमेंटल परंपराओं और कल्याणकारी पहलों का कुशल मार्गदर्शन किया।",
        "writeup_pa": "ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਜੇਸੀ ਕਪੂਰ ਨੇ ਅਗਸਤ 1948 ਵਿੱਚ ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਐਮਐਮ ਬਾਦਸ਼ਾਹ ਤੋਂ ਬਾਅਦ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੇ ਦੂਜੇ ਭਾਰਤੀ ਕਮਾਂਡੈਂਟ ਵਜੋਂ ਕਮਾਂਡ ਸੰਭਾਲੀ। ਜਨਵਰੀ 1950 ਤੱਕ ਆਪਣੇ ਕਾਰਜਕਾਲ ਦੌਰਾਨ, ਉਨ੍ਹਾਂ ਨੇ ਆਜ਼ਾਦੀ ਤੋਂ ਬਾਅਦ ਭਾਰਤੀ ਫੌਜ ਦੇ ਪੁਨਰਗਠਨ ਸਮੇਂ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੇ ਸਿਖਲਾਈ ਬੁਨਿਆਦੀ ਢਾਂਚੇ ਅਤੇ ਪ੍ਰਬੰਧਕੀ ਆਧਾਰ ਨੂੰ ਮਜ਼ਬੂਤ ਕੀਤਾ। ਉਨ੍ਹਾਂ ਨੇ ਰੈਜੀਮੈਂਟ ਦੇ ਆਧੁਨਿਕ ਯੁੱਗ ਦੇ ਸ਼ੁਰੂਆਤੀ ਸਾਲਾਂ ਵਿੱਚ ਰੰਗਰੂਟਾਂ ਦੀ ਸਿਖਲਾਈ ਅਤੇ ਰੈਜੀਮੈਂਟਲ ਰਵਾਇਤਾਂ ਦੀ ਅਗਵਾਈ ਕੀਤੀ।"
    },
    {
        "art_num": 42,
        "title_en": "Lieutenant Colonel HS Gill",
        "title_hi": "लेफ्टिनेंट कर्नल एचएस गिल",
        "title_pa": "ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਐਚਐਸ ਗਿੱਲ",
        "year_en": "January 1950 - March 1950",
        "year_hi": "जनवरी 1950 - मार्च 1950",
        "year_pa": "ਜਨਵਰੀ 1950 - ਮਾਰਚ 1950",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "LIEUTENANT COLONEL HS GILL (January 1950 - March 1950)",
        "header_hi": "लेफ्टिनेंट कर्नल एचएस गिल (जनवरी 1950 - मार्च 1950)",
        "header_pa": "ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਐਚਐਸ ਗਿੱਲ (ਜਨਵਰੀ 1950 - ਮਾਰਚ 1950)",
        "writeup_en": "Lieutenant Colonel Harchand Singh Gill was commissioned into 3 SIKH on 03 January 1940 and later commanded the Battalion. During the intense fighting in Jammu and Kashmir in 1947–48, he commanded 3 SIKH with exceptional gallantry, capturing Richhmar Gali in the face of heavy enemy opposition. He served as Commandant of the Sikh Regimental Centre from January to March 1950. He was also an accomplished horse rider, polo player, and all-round sportsman.",
        "writeup_hi": "लेफ्टिनेंट कर्नल हरचंद सिंह गिल 3 जनवरी 1940 को 3 सिख में कमीशन हुए थे और बाद में उन्होंने बटालियन की कमान संभाली। 1947-48 में जम्मू-कश्मीर के भीषण युद्ध के दौरान, उन्होंने असाधारण वीरता के साथ 3 सिख की कमान संभालते हुए रीछमार गली पर विजय प्राप्त की। उन्होंने जनवरी से मार्च 1950 तक सिख रेजिमेंटल सेंटर के कमांडेंट के रूप में सेवा दी। वह एक कुशल घुड़सवार, पोलो खिलाड़ी और उत्कृष्ट खिलाड़ी भी थे।",
        "writeup_pa": "ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਹਰਚੰਦ ਸਿੰਘ ਗਿੱਲ 3 ਜਨਵਰੀ 1940 ਨੂੰ 3 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਸਨ ਅਤੇ ਬਾਅਦ ਵਿੱਚ ਬਟਾਲੀਅਨ ਦੀ ਕਮਾਂਡ ਸੰਭਾਲੀ। 1947-48 ਵਿੱਚ ਜੰਮੂ ਅਤੇ ਕਸ਼ਮੀਰ ਦੀਆਂ ਲੜਾਈਆਂ ਦੌਰਾਨ, ਉਨ੍ਹਾਂ ਨੇ ਬੇਮਿਸਾਲ ਬਹਾਦਰੀ ਨਾਲ 3 ਸਿੱਖ ਦੀ ਅਗਵਾਈ ਕਰਦਿਆਂ ਰਿਛਮਾਰ ਗਲੀ 'ਤੇ ਕਬਜ਼ਾ ਕੀਤਾ। ਉਨ੍ਹਾਂ ਨੇ ਜਨਵਰੀ ਤੋਂ ਮਾਰਚ 1950 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੇ ਕਮਾਂਡੈਂਟ ਵਜੋਂ ਸੇਵਾ ਨਿਭਾਈ। ਉਹ ਇੱਕ ਉੱਘੇ ਘੋੜਸਵਾਰ, ਪੋਲੋ ਖਿਡਾਰੀ ਅਤੇ ਉੱਤਮ ਅਥਲੀਟ ਵੀ ਸਨ।"
    },
    {
        "art_num": 43,
        "title_en": "Lieutenant Colonel Budh Singh, MC",
        "title_hi": "लेफ्टिनेंट कर्नल बुध सिंह, एमसी",
        "title_pa": "ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਬੁੱਧ ਸਿੰਘ, ਐਮਸੀ",
        "year_en": "March 1950 - March 1953",
        "year_hi": "मार्च 1950 - मार्च 1953",
        "year_pa": "ਮਾਰਚ 1950 - ਮਾਰਚ 1953",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "LIEUTENANT COLONEL BUDH SINGH, MC (March 1950 - March 1953)",
        "header_hi": "लेफ्टिनेंट कर्नल बुध सिंह, एमसी (मार्च 1950 - मार्च 1953)",
        "header_pa": "ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਬੁੱਧ ਸਿੰਘ, ਐਮਸੀ (ਮਾਰਚ 1950 - ਮਾਰਚ 1953)",
        "writeup_en": "Lieutenant Colonel Budh Singh was commissioned into 1 SIKH on 15 July 1938. During the Second World War in Burma, he was awarded the Military Cross for outstanding leadership and bravery. He commanded the Sikh Regimental Centre at Ambala from March 1950 to March 1953. During his tenure, the Regimental Centre made substantial progress in military training standards, sports achievements, and the preservation of regimental heritage.",
        "writeup_hi": "लेफ्टिनेंट कर्नल बुध सिंह 15 जुलाई 1938 को 1 सिख में कमीशन हुए थे। द्वितीय विश्व युद्ध के दौरान बर्मा में अदम्य साहस और उत्कृष्ट नेतृत्व के लिए उन्हें प्रतिष्ठित मिलिट्री क्रॉस से सम्मानित किया गया था। उन्होंने मार्च 1950 से मार्च 1953 तक अंबाला में सिख रेजिमेंटल सेंटर की कमान संभाली। उनके कार्यकाल के दौरान सेंटर ने सैन्य प्रशिक्षण, खेल प्रतियोगिताओं और रेजिमेंटल विरासत के संरक्षण में महत्वपूर्ण प्रगति हासिल की।",
        "writeup_pa": "ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਬੁੱਧ ਸਿੰਘ 15 ਜੁਲਾਈ 1938 ਨੂੰ 1 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਸਨ। ਦੂਜੇ ਵਿਸ਼ਵ ਯੁੱਧ ਦੌਰਾਨ ਬਰਮਾ ਵਿੱਚ ਸ਼ਾਨਦਾਰ ਅਗਵਾਈ ਅਤੇ ਦਲੇਰੀ ਲਈ ਉਨ੍ਹਾਂ ਨੂੰ ਮਿਲਟਰੀ ਕਰਾਸ ਨਾਲ ਸਨਮਾਨਿਤ ਕੀਤਾ ਗਿਆ। ਉਨ੍ਹਾਂ ਨੇ ਮਾਰਚ 1950 ਤੋਂ ਮਾਰਚ 1953 ਤੱਕ ਅੰਬਾਲਾ ਵਿਖੇ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਕਮਾਂਡ ਸੰਭਾਲੀ। ਉਨ੍ਹਾਂ ਦੇ ਕਾਰਜਕਾਲ ਦੌਰਾਨ ਸੈਂਟਰ ਨੇ ਸਿਖਲਾਈ ਮਿਆਰਾਂ, ਖੇਡਾਂ ਅਤੇ ਰੈਜੀਮੈਂਟਲ ਵਿਰਾਸਤ ਦੀ ਸਾਂਭ-ਸੰਭਾਲ ਵਿੱਚ ਸ਼ਾਨਦਾਰ ਤਰੱਕੀ ਕੀਤੀ।"
    },
    {
        "art_num": 44,
        "title_en": "Lieutenant Colonel Girdhari Singh, VrC, MC",
        "title_hi": "लेफ्टिनेंट कर्नल गिरधारी सिंह, वीआरसी, एमसी",
        "title_pa": "ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਗਿਰਧਾਰੀ ਸਿੰਘ, ਵੀਆਰਸੀ, ਐਮਸੀ",
        "year_en": "March 1953 - August 1959",
        "year_hi": "मार्च 1953 - अगस्त 1959",
        "year_pa": "ਮਾਰਚ 1953 - ਅਗਸਤ 1959",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "LIEUTENANT COLONEL GIRDHARI SINGH, VrC, MC (March 1953 - August 1959)",
        "header_hi": "लेफ्टिनेंट कर्नल गिरधारी सिंह, वीआरसी, एमसी (मार्च 1953 - अगस्त 1959)",
        "header_pa": "ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਗਿਰਧਾਰੀ ਸਿੰਘ, ਵੀਆਰਸੀ, ਐਮਸੀ (ਮਾਰਚ 1953 - ਅਗਸਤ 1959)",
        "writeup_en": "Lieutenant Colonel Girdhari Singh, VrC, MC, had one of the longest and most distinguished tenures as Commandant of the Sikh Regimental Centre, serving at Meerut from March 1953 to August 1959. A highly decorated war veteran who earned both the Military Cross and the Vir Chakra, he was an exceptional administrator, disciplinarian, and sportsman. His leadership left an indelible mark on regimental institutions, training ethos, and infrastructure at Meerut.",
        "writeup_hi": "लेफ्टिनेंट कर्नल गिरधारी सिंह, वीर चक्र, मिलिट्री क्रॉस, ने मार्च 1953 से अगस्त 1959 तक मेरठ में सिख रेजिमेंटल सेंटर के कमांडेंट के रूप में सबसे लंबा और प्रतिष्ठित कार्यकाल पूरा किया। मिलिट्री क्रॉस और वीर चक्र दोनों से अलंकृत इस वीर योद्धा ने एक उत्कृष्ट प्रशासक, अनुशासनप्रिय और कुशल खिलाड़ी के रूप में अमिट छाप छोड़ी। उनके नेतृत्व ने मेरठ में रेजिमेंटल संस्थाओं, प्रशिक्षण और बुनियादी ढांचे को नई ऊंचाइयां दीं।",
        "writeup_pa": "ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਗਿਰਧਾਰੀ ਸਿੰਘ, ਵੀਰ ਚੱਕਰ, ਮਿਲਟਰੀ ਕਰਾਸ, ਨੇ ਮਾਰਚ 1953 ਤੋਂ ਅਗਸਤ 1959 ਤੱਕ ਮੇਰਠ ਵਿਖੇ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੇ ਕਮਾਂਡੈਂਟ ਵਜੋਂ ਸਭ ਤੋਂ ਲੰਮਾ ਅਤੇ ਸ਼ਾਨਦਾਰ ਕਾਰਜਕਾਲ ਨਿਭਾਇਆ। ਮਿਲਟਰੀ ਕਰਾਸ ਅਤੇ ਵੀਰ ਚੱਕਰ ਦੋਵਾਂ ਨਾਲ ਸਨਮਾਨਿਤ ਇਸ ਬਹਾਦਰ ਯੋਧੇ ਨੇ ਰੈਜੀਮੈਂਟਲ ਸੰਸਥਾਵਾਂ, ਅਨੁਸ਼ਾਸਨ, ਖੇਡਾਂ ਅਤੇ ਸਿਖਲਾਈ ਢਾਂਚੇ 'ਤੇ ਇੱਕ ਅਮਿੱਟ ਛਾਪ ਛੱਡੀ।"
    },
    {
        "art_num": 45,
        "title_en": "Colonel Shamsher Singh",
        "title_hi": "कर्नल शमशेर सिंह",
        "title_pa": "ਕਰਨਲ ਸ਼ਮਸ਼ੇਰ ਸਿੰਘ",
        "year_en": "August 1959 - October 1963 & July 1965 - June 1966",
        "year_hi": "अगस्त 1959 - अक्टूबर 1963 एवं जुलाई 1965 - जून 1966",
        "year_pa": "ਅਗਸਤ 1959 - ਅਕਤੂਬਰ 1963 ਅਤੇ ਜੁਲਾਈ 1965 - ਜੂਨ 1966",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "COLONEL SHAMSHER SINGH (August 1959 - October 1963 & July 1965 - June 1966)",
        "header_hi": "कर्नल शमशेर सिंह (अगस्त 1959 - अक्टूबर 1963 एवं जुलाई 1965 - जून 1966)",
        "header_pa": "ਕਰਨਲ ਸ਼ਮਸ਼ੇਰ ਸਿੰਘ (ਅਗਸਤ 1959 - ਅਕਤੂਬਰ 1963 ਅਤੇ ਜੁਲਾਈ 1965 - ਜੂਨ 1966)",
        "writeup_en": "Colonel Shamsher Singh was commissioned in July 1941 into the 8th Punjab Regiment and transferred to 2 SIKH during Partition. He commanded 2 SIKH in the Sino-Indian War of 1962 and had the rare distinction of commanding the Sikh Regimental Centre twice, from August 1959 to October 1963 and from July 1965 to June 1966. He was renowned for raising operational standards and mentoring generations of brave Sikh soldiers.",
        "writeup_hi": "कर्नल शमशेर सिंह जुलाई 1941 में 8वीं पंजाब रेजिमेंट में कमीशन हुए और विभाजन के समय 2 सिख में स्थानांतरित हुए। उन्होंने 1962 के भारत-चीन युद्ध में 2 सिख की कमान संभाली और अगस्त 1959 से अक्टूबर 1963 तथा जुलाई 1965 से जून 1966 तक दो बार सिख रेजिमेंटल सेंटर की कमान संभालने का दुर्लभ गौरव हासिल किया। उन्होंने सेंटर के परिचालन और प्रशिक्षण मानकों को नई मजबूती प्रदान की।",
        "writeup_pa": "ਕਰਨਲ ਸ਼ਮਸ਼ੇਰ ਸਿੰਘ ਜੁਲਾਈ 1941 ਵਿੱਚ 8ਵੀਂ ਪੰਜਾਬ ਰੈਜੀਮੈਂਟ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਅਤੇ ਵੰਡ ਵੇਲੇ 2 ਸਿੱਖ ਵਿੱਚ ਤਬਦੀਲ ਹੋਏ। ਉਨ੍ਹਾਂ ਨੇ 1962 ਦੀ ਜੰਗ ਵਿੱਚ 2 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ ਅਤੇ ਅਗਸਤ 1959 ਤੋਂ ਅਕਤੂਬਰ 1963 ਅਤੇ ਜੁਲਾਈ 1965 ਤੋਂ ਜੂਨ 1966 ਤੱਕ ਦੋ ਵਾਰ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਕਮਾਂਡ ਕਰਨ ਦਾ ਮਾਣ ਹਾਸਲ ਕੀਤਾ। ਉਨ੍ਹਾਂ ਨੇ ਰੈਜੀਮੈਂਟ ਦੀਆਂ ਸਿਖਲਾਈ ਪਰੰਪਰਾਵਾਂ ਨੂੰ ਬਹੁਤ ਮਜ਼ਬੂਤ ਕੀਤਾ।"
    },
    {
        "art_num": 46,
        "title_en": "Colonel BS Bajwa, MC",
        "title_hi": "कर्नल बीएस बाजवा, एमसी",
        "title_pa": "ਕਰਨਲ ਬੀਐਸ ਬਾਜਵਾ, ਐਮਸੀ",
        "year_en": "October 1963 - June 1965",
        "year_hi": "अक्टूबर 1963 - जून 1965",
        "year_pa": "ਅਕਤੂਬਰ 1963 - ਜੂਨ 1965",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "COLONEL BS BAJWA, MC (October 1963 - June 1965)",
        "header_hi": "कर्नल बीएस बाजवा, एमसी (अक्टूबर 1963 - जून 1965)",
        "header_pa": "ਕਰਨਲ ਬੀਐਸ ਬਾਜਵਾ, ਐਮਸੀ (ਅਕਤੂਬਰ 1963 - ਜੂਨ 1965)",
        "writeup_en": "Colonel Buta Singh Bajwa was a battle-hardened officer awarded the Military Cross during World War II. He commanded 4 SIKH, 3 SIKH, and 124 Infantry Battalion (TA). He served as Commandant of the Sikh Regimental Centre from October 1963 to June 1965. During his tenure, the Regimental Centre underwent rapid expansion and intense training enhancements following the 1962 War, preparing battalions for future operational readiness.",
        "writeup_hi": "कर्नल बूटा सिंह बाजवा द्वितीय विश्व युद्ध में मिलिट्री क्रॉस से सम्मानित एक अनुभवी योद्धा थे। उन्होंने 4 सिख, 3 सिख और 124 इन्फैंट्री बटालियन (टीए) की कमान संभाली। उन्होंने अक्टूबर 1963 से जून 1965 तक सिख रेजिमेंटल सेंटर के कमांडेंट के रूप में सेवा दी। 1962 के युद्ध के बाद उनके कार्यकाल में सेंटर का तीव्र विस्तार हुआ और बटालियनों की युद्धक तैयारी के लिए व्यापक प्रशिक्षण सुधार किए गए।",
        "writeup_pa": "ਕਰਨਲ ਬੂਟਾ ਸਿੰਘ ਬਾਜਵਾ ਦੂਜੇ ਵਿਸ਼ਵ ਯੁੱਧ ਦੌਰਾਨ ਮਿਲਟਰੀ ਕਰਾਸ ਨਾਲ ਸਨਮਾਨਿਤ ਇੱਕ ਬਹਾਦਰ ਅਧਿਕਾਰੀ ਸਨ। ਉਨ੍ਹਾਂ ਨੇ 4 ਸਿੱਖ, 3 ਸਿੱਖ ਅਤੇ 124 ਇਨਫੈਂਟਰੀ ਬਟਾਲੀਅਨ (ਟੀਏ) ਦੀ ਕਮਾਂਡ ਕੀਤੀ। ਉਨ੍ਹਾਂ ਨੇ ਅਕਤੂਬਰ 1963 ਤੋਂ ਜੂਨ 1965 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੇ ਕਮਾਂਡੈਂਟ ਵਜੋਂ ਸੇਵਾ ਨਿਭਾਈ। 1962 ਦੀ ਜੰਗ ਤੋਂ ਬਾਅਦ ਉਨ੍ਹਾਂ ਦੇ ਕਾਰਜਕਾਲ ਵਿੱਚ ਸੈਂਟਰ ਦਾ ਤੇਜ਼ੀ ਨਾਲ ਵਿਸਥਾਰ ਹੋਇਆ ਅਤੇ ਜੰਗੀ ਤਿਆਰੀਆਂ ਮਜ਼ਬੂਤ ਕੀਤੀਆਂ ਗਈਆਂ।"
    },
    {
        "art_num": 47,
        "title_en": "Colonel Gurbaksh Singh",
        "title_hi": "कर्नल गुरबख्श सिंह",
        "title_pa": "ਕਰਨਲ ਗੁਰਬਖਸ਼ ਸਿੰਘ",
        "year_en": "June 1966 - July 1970",
        "year_hi": "जून 1966 - जुलाई 1970",
        "year_pa": "ਜੂਨ 1966 - ਜੁਲਾਈ 1970",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "COLONEL GURBAKSH SINGH (June 1966 - July 1970)",
        "header_hi": "कर्नल गुरबख्श सिंह (जून 1966 - जुलाई 1970)",
        "header_pa": "ਕਰਨਲ ਗੁਰਬਖਸ਼ ਸਿੰਘ (ਜੂਨ 1966 - ਜੁਲਾਈ 1970)",
        "writeup_en": "Colonel Gurbaksh Singh was commissioned in September 1942 into 3 SIKH and served in Eritrea and Japan. He commanded 7 SIKH in Ladakh during the 1962 conflict and led the Sikh Regimental Centre as Commandant from June 1966 to July 1970. He brought immense dynamism to recruit training, weapon handling, and physical fitness, establishing institutions that modernized the Centre's administrative and operational capabilities.",
        "writeup_hi": "कर्नल गुरबख्श सिंह सितंबर 1942 में 3 सिख में कमीशन हुए और इरिट्रिया तथा जापान में सेवाएं दीं। उन्होंने 1962 के युद्ध में लद्दाख में 7 सिख की कमान संभाली और जून 1966 से जुलाई 1970 तक सिख रेजिमेंटल सेंटर के कमांडेंट रहे। उन्होंने रंगरूट प्रशिक्षण, हथियार संचालन और शारीरिक फिटनेस में आधुनिक पद्धतियां लागू कीं तथा सेंटर की प्रशासनिक क्षमताओं को सुदृढ़ किया।",
        "writeup_pa": "ਕਰਨਲ ਗੁਰਬਖਸ਼ ਸਿੰਘ ਸਤੰਬਰ 1942 ਵਿੱਚ 3 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਅਤੇ ਇਰੀਟਰੀਆ ਤੇ ਜਾਪਾਨ ਵਿੱਚ ਸੇਵਾ ਨਿਭਾਈ। ਉਨ੍ਹਾਂ ਨੇ 1962 ਦੀ ਜੰਗ ਵਿੱਚ ਲੱਦਾਖ ਵਿਖੇ 7 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ ਅਤੇ ਜੂਨ 1966 ਤੋਂ ਜੁਲਾਈ 1970 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੇ ਕਮਾਂਡੈਂਟ ਰਹੇ। ਉਨ੍ਹਾਂ ਨੇ ਰੰਗਰੂਟਾਂ ਦੀ ਸਿਖਲਾਈ, ਹਥਿਆਰਾਂ ਦੀ ਵਰਤੋਂ ਅਤੇ ਸਰੀਰਕ ਤੰਦਰੁਸਤੀ ਵਿੱਚ ਸ਼ਾਨਦਾਰ ਸੁਧਾਰ ਕੀਤੇ।"
    },
    {
        "art_num": 48,
        "title_en": "Colonel RC Puri",
        "title_hi": "कर्नल आरसी पुरी",
        "title_pa": "ਕਰਨਲ ਆਰਸੀ ਪੁਰੀ",
        "year_en": "July 1970 - October 1974",
        "year_hi": "जुलाई 1970 - अक्टूबर 1974",
        "year_pa": "ਜੁਲਾਈ 1970 - ਅਕਤੂਬਰ 1974",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "COLONEL RC PURI (July 1970 - October 1974)",
        "header_hi": "कर्नल आरसी पुरी (जुलाई 1970 - अक्टूबर 1974)",
        "header_pa": "ਕਰਨਲ ਆਰਸੀ ਪੁਰੀ (ਜੁਲਾਈ 1970 - ਅਕਤੂਬਰ 1974)",
        "writeup_en": "Colonel Ramesh Chand Puri was commissioned on 12 September 1948 and commanded 7 SIKH from 1965 to 1968. He commanded the Sikh Regimental Centre from July 1970 to October 1974, steering the Centre with distinction through the historic 1971 Indo-Pak War. Under his stewardship, the Centre mobilized battalions, provided reinforcements, and organized hero welcomes for decorated war veterans.",
        "writeup_hi": "कर्नल रमेश चंद पुरी 12 सितंबर 1948 को कमीशन हुए और 1965 से 1968 तक 7 सिख की कमान संभाली। उन्होंने जुलाई 1970 से अक्टूबर 1974 तक सिख रेजिमेंटल सेंटर की कमान संभाली और ऐतिहासिक 1971 के भारत-पाक युद्ध के दौरान सेंटर का कुशल नेतृत्व किया। उनके मार्गदर्शन में सेंटर ने बटालियनों को सुदृढ़ किया और युद्ध नायकों का सम्मान किया।",
        "writeup_pa": "ਕਰਨਲ ਰਮੇਸ਼ ਚੰਦ ਪੁਰੀ 12 ਸਤੰਬਰ 1948 ਨੂੰ ਕਮਿਸ਼ਨ ਹੋਏ ਅਤੇ 1965 ਤੋਂ 1968 ਤੱਕ 7 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ। ਉਨ੍ਹਾਂ ਨੇ ਜੁਲਾਈ 1970 ਤੋਂ ਅਕਤੂਬਰ 1974 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਕਮਾਂਡ ਸੰਭਾਲੀ ਅਤੇ ਇਤਿਹਾਸਕ 1971 ਦੀ ਭਾਰਤ-ਪਾਕਿ ਜੰਗ ਦੌਰਾਨ ਸੈਂਟਰ ਦੀ ਸ਼ਾਨਦਾਰ ਅਗਵਾਈ ਕੀਤੀ।"
    },
    {
        "art_num": 49,
        "title_en": "Colonel BB Upreti, AVSM, VSM",
        "title_hi": "कर्नल बीबी उप्रेती, एवीएसएम, वीएसएम",
        "title_pa": "ਕਰਨਲ ਬੀਬੀ ਉਪਰੇਤੀ, ਏਵੀਐਸਐਮ, ਵੀਐਸਐਮ",
        "year_en": "October 1974 - April 1978",
        "year_hi": "अक्टूबर 1974 - अप्रैल 1978",
        "year_pa": "ਅਕਤੂਬਰ 1974 - ਅਪ੍ਰੈਲ 1978",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "COLONEL BB UPRETI, AVSM, VSM (October 1974 - April 1978)",
        "header_hi": "कर्नल बीबी उप्रेती, एवीएसएम, वीएसएम (अक्टूबर 1974 - अप्रैल 1978)",
        "header_pa": "ਕਰਨਲ ਬੀਬੀ ਉਪਰੇਤੀ, ਏਵੀਐਸਐਮ, ਵੀਐਸਐਮ (ਅਕਤੂਬਰ 1974 - ਅਪ੍ਰੈਲ 1978)",
        "writeup_en": "Colonel Basant Ballabh Upreti was commissioned into 7 SIKH on 28 December 1952. He commanded 7 SIKH in Counter Insurgency Operations in Nagaland and later commanded the Sikh Regimental Centre from October 1974 to April 1978. Awarded the AVSM and VSM, he modernized training syllabi, established modern living facilities, and raised the overall administrative efficiency of the Regimental Centre.",
        "writeup_hi": "कर्नल बसंत बल्लभ उप्रेती 28 दिसंबर 1952 को 7 सिख में कमीशन हुए। उन्होंने नागालैंड में उग्रवाद-विरोधी अभियानों में 7 सिख की कमान संभाली और अक्टूबर 1974 से अप्रैल 1978 तक सिख रेजिमेंटल सेंटर के कमांडेंट रहे। एवीएसएम और वीएसएम से सम्मानित, उन्होंने प्रशिक्षण पाठ्यक्रम को आधुनिक बनाया और जवानों के लिए उत्कृष्ट सुविधाएं स्थापित कीं।",
        "writeup_pa": "ਕਰਨਲ ਬਸੰਤ ਬੱਲਭ ਉਪਰੇਤੀ 28 ਦਸੰਬਰ 1952 ਨੂੰ 7 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ। ਉਨ੍ਹਾਂ ਨੇ ਨਾਗਾਲੈਂਡ ਵਿੱਚ ਅੱਤਵਾਦ ਵਿਰੋਧੀ ਕਾਰਵਾਈਆਂ ਦੌਰਾਨ 7 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ ਅਤੇ ਅਕਤੂਬਰ 1974 ਤੋਂ ਅਪ੍ਰੈਲ 1978 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੇ ਕਮਾਂਡੈਂਟ ਰਹੇ। ਏਵੀਐਸਐਮ ਅਤੇ ਵੀਐਸਐਮ ਨਾਲ ਸਨਮਾਨਿਤ, ਉਨ੍ਹਾਂ ਨੇ ਸਿਖਲਾਈ ਪ੍ਰਣਾਲੀ ਅਤੇ ਸਹੂਲਤਾਂ ਦਾ ਆਧੁਨਿਕੀਕਰਨ ਕੀਤਾ।"
    },
    {
        "art_num": 50,
        "title_en": "Colonel KC Kalley, VSM",
        "title_hi": "कर्नल केसी काले, वीएसएम",
        "title_pa": "ਕਰਨਲ ਕੇਸੀ ਕਾਲੇ, ਵੀਐਸਐਮ",
        "year_en": "April 1978 - July 1981",
        "year_hi": "अप्रैल 1978 - जुलाई 1981",
        "year_pa": "ਅਪ੍ਰੈਲ 1978 - ਜੁਲਾਈ 1981",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "COLONEL KC KALLEY, VSM (April 1978 - July 1981)",
        "header_hi": "कर्नल केसी काले, वीएसएम (अप्रैल 1978 - जुलाई 1981)",
        "header_pa": "ਕਰਨਲ ਕੇਸੀ ਕਾਲੇ, ਵੀਐਸਐਮ (ਅਪ੍ਰੈਲ 1978 - ਜੁਲਾਈ 1981)",
        "writeup_en": "Colonel Kailash Chandra Kalley was commissioned into 2 SIKH on 06 June 1954. He commanded 2 SIKH and 10 SIKH, leading 10 SIKH during the 1971 Indo-Pak War. He commanded the Sikh Regimental Centre from April 1978 to July 1981, receiving the Vishisht Seva Medal. He initiated the landmark transition and planning for shifting the Regimental Centre to its permanent location in Ramgarh.",
        "writeup_hi": "कर्नल कैलाश चंद्र काले 6 जून 1954 को 2 सिख में कमीशन हुए। उन्होंने 2 सिख और 10 सिख की कमान संभाली तथा 1971 के युद्ध में 10 सिख का नेतृत्व किया। उन्होंने अप्रैल 1978 से जुलाई 1981 तक सिख रेजिमेंटल सेंटर की कमान संभाली और विशिष्ट सेवा मेडल प्राप्त किया। उन्होंने सेंटर को रामगढ़ स्थित स्थायी स्थान पर स्थानांतरित करने की ऐतिहासिक योजना का नेतृत्व किया।",
        "writeup_pa": "ਕਰਨਲ ਕੈਲਾਸ਼ ਚੰਦਰ ਕਾਲੇ 6 ਜੂਨ 1954 ਨੂੰ 2 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ। ਉਨ੍ਹਾਂ ਨੇ 2 ਸਿੱਖ ਅਤੇ 10 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ ਅਤੇ 1971 ਦੀ ਜੰਗ ਵਿੱਚ 10 ਸਿੱਖ ਦੀ ਅਗਵਾਈ ਕੀਤੀ। ਉਨ੍ਹਾਂ ਨੇ ਅਪ੍ਰੈਲ 1978 ਤੋਂ ਜੁਲਾਈ 1981 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਕਮਾਂਡ ਕੀਤੀ ਅਤੇ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਨੂੰ ਰਾਮਗੜ੍ਹ ਵਿਖੇ ਪੱਕੇ ਤੌਰ 'ਤੇ ਤਬਦੀਲ ਕਰਨ ਦੀ ਯੋਜਨਾ ਸ਼ੁਰੂ ਕੀਤੀ।"
    },
    {
        "art_num": 51,
        "title_en": "Brigadier SC Puri",
        "title_hi": "ब्रिगेडियर एससी पुरी",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਐਸਸੀ ਪੁਰੀ",
        "year_en": "July 1981 - June 1984",
        "year_hi": "जुलाई 1981 - जून 1984",
        "year_pa": "ਜੁਲਾਈ 1981 - ਜੂਨ 1984",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER SC PURI (July 1981 - June 1984)",
        "header_hi": "ब्रिगेडियर एससी पुरी (जुलाई 1981 - जून 1984)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਐਸਸੀ ਪੁਰੀ (ਜੁਲਾਈ 1981 - ਜੂਨ 1984)",
        "writeup_en": "Brigadier Suresh Chandra Puri was commissioned into 2 SIKH on 06 June 1954 and commanded the Battalion from 1969 to 1973. He commanded the Sikh Regimental Centre from July 1981 until his untimely demise in June 1984. During his tenure, he achieved the momentous task of moving the Regimental Centre from Meerut to Ramgarh, establishing the foundation of the permanent regimental home.",
        "writeup_hi": "ब्रिगेडियर सुरेश चंद्र पुरी 6 जून 1954 को 2 सिख में कमीशन हुए और 1969 से 1973 तक बटालियन की कमान संभाली। उन्होंने जुलाई 1981 से जून 1984 तक सिख रेजिमेंटल सेंटर की कमान संभाली। अपने कार्यकाल के दौरान उन्होंने रेजिमेंटल सेंटर को मेरठ से रामगढ़ स्थानांतरित करने का ऐतिहासिक कार्य पूरा किया और स्थायी रेजिमेंटल घर की मजबूत नींव रखी।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਸੁਰੇਸ਼ ਚੰਦਰ ਪੁਰੀ 6 ਜੂਨ 1954 ਨੂੰ 2 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਅਤੇ 1969 ਤੋਂ 1973 ਤੱਕ ਬਟਾਲੀਅਨ ਦੀ ਕਮਾਂਡ ਕੀਤੀ। ਉਨ੍ਹਾਂ ਨੇ ਜੁਲਾਈ 1981 ਤੋਂ ਜੂਨ 1984 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਕਮਾਂਡ ਸੰਭਾਲੀ। ਉਨ੍ਹਾਂ ਦੇ ਕਾਰਜਕਾਲ ਦੌਰਾਨ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਨੂੰ ਮੇਰਠ ਤੋਂ ਰਾਮਗੜ੍ਹ ਤਬਦੀਲ ਕਰਨ ਦਾ ਇਤਿਹਾਸਕ ਕਾਰਜ ਸਫਲਤਾਪੂਰਵਕ ਨੇਪਰੇ ਚੜ੍ਹਿਆ।"
    },
    {
        "art_num": 52,
        "title_en": "Brigadier MMS Vasir, AVSM",
        "title_hi": "ब्रिगेडियर एमएमएस वसीर, एवीएसएम",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਐਮਐਮਐਸ ਵਸੀਰ, ਏਵੀਐਸਐਮ",
        "year_en": "July 1984 - February 1986",
        "year_hi": "जुलाई 1984 - फरवरी 1986",
        "year_pa": "ਜੁਲਾਈ 1984 - ਫਰਵਰੀ 1986",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER MMS VASIR, AVSM (July 1984 - February 1986)",
        "header_hi": "ब्रिगेडियर एमएमएस वसीर, एवीएसएम (जुलाई 1984 - फरवरी 1986)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਐਮਐਮਐਸ ਵਸੀਰ, ਏਵੀਐਸਐਮ (ਜੁਲਾਈ 1984 - ਫਰਵਰੀ 1986)",
        "writeup_en": "Brigadier Man Mohan Singh Vasir was commissioned into 5 SIKH on 12 June 1960. He commanded 16 SIKH in Counter Insurgency Operations and served as Instructor at the Indian Military Academy. He took command of the Sikh Regimental Centre in July 1984 during testing times, steering it until February 1986. Awarded the AVSM, he consolidated the Centre's permanent infrastructure at Ramgarh and revitalized regimental traditions.",
        "writeup_hi": "ब्रिगेडियर मन मोहन सिंह वसीर 12 जून 1960 को 5 सिख में कमीशन हुए। उन्होंने उग्रवाद-विरोधी अभियानों में 16 सिख की कमान संभाली और आईएमए में प्रशिक्षक रहे। उन्होंने जुलाई 1984 से फरवरी 1986 तक चुनौतीपूर्ण समय में सिख रेजिमेंटल सेंटर की कमान संभाली। एवीएसएम से सम्मानित, उन्होंने रामगढ़ में सेंटर के बुनियादी ढांचे को मजबूत किया और रेजिमेंटल परंपराओं को पुनर्जीवित किया।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਮਨ ਮੋਹਨ ਸਿੰਘ ਵਸੀਰ 12 ਜੂਨ 1960 ਨੂੰ 5 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ। ਉਨ੍ਹਾਂ ਨੇ 16 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ ਅਤੇ ਆਈਐਮਏ ਵਿਖੇ ਇੰਸਟ੍ਰਕਟਰ ਵਜੋਂ ਸੇਵਾ ਕੀਤੀ। ਉਨ੍ਹਾਂ ਨੇ ਜੁਲਾਈ 1984 ਤੋਂ ਫਰਵਰੀ 1986 ਤੱਕ ਚੁਣੌਤੀਪੂਰਨ ਸਮੇਂ ਵਿੱਚ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਕਮਾਂਡ ਕੀਤੀ। ਏਵੀਐਸਐਮ ਨਾਲ ਸਨਮਾਨਿਤ, ਉਨ੍ਹਾਂ ਨੇ ਰਾਮਗੜ੍ਹ ਵਿਖੇ ਬੁਨਿਆਦੀ ਢਾਂਚੇ ਅਤੇ ਰਵਾਇਤਾਂ ਨੂੰ ਮਜ਼ਬੂਤ ਕੀਤਾ।"
    },
    {
        "art_num": 53,
        "title_en": "Brigadier CS Nugyal, PVSM, UYSM",
        "title_hi": "ब्रिगेडियर सीएस नुग्याल, पीवीएसएम, यूवाईएसएम",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਸੀਐਸ ਨੁਗਿਆਲ, ਪੀਵੀਐਸਐਮ, ਯੂਵਾਈਐਸਐਮ",
        "year_en": "February 1986 - December 1986",
        "year_hi": "फरवरी 1986 - दिसंबर 1986",
        "year_pa": "ਫਰਵਰੀ 1986 - ਦਸੰਬਰ 1986",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER CS NUGYAL, PVSM, UYSM (February 1986 - December 1986)",
        "header_hi": "ब्रिगेडियर सीएस नुग्याल, पीवीएसएम, यूवाईएसएम (फरवरी 1986 - दिसंबर 1986)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਸੀਐਸ ਨੁਗਿਆਲ, ਪੀਵੀਐਸਐਮ, ਯੂਵਾਈਐਸਐਮ (ਫਰਵਰੀ 1986 - ਦਸੰਬਰ 1986)",
        "writeup_en": "Brigadier Chandan Singh Nugyal was commissioned into 6 SIKH on 17 December 1961 and commanded the unit in Counter Insurgency and High Altitude environments. He commanded the Sikh Regimental Centre from February to December 1986. Later rising to Lieutenant General with PVSM and UYSM decorations, his dynamic vision at SRC focused on recruit soldiering ethos, field craft, and sports development.",
        "writeup_hi": "ब्रिगेडियर चंदन सिंह नुग्याल 17 दिसंबर 1961 को 6 सिख में कमीशन हुए और उन्होंने उग्रवाद-विरोधी तथा उच्च तुंगता क्षेत्रों में बटालियन की कमान संभाली। उन्होंने फरवरी से दिसंबर 1986 तक सिख रेजिमेंटल सेंटर की कमान संभाली। बाद में लेफ्टिनेंट जनरल के पद पर पदोन्नत होकर पीवीएसएम और यूवाईएसएम से अलंकृत, उन्होंने सेंटर में युद्ध कौशल और खेल विकास पर विशेष जोर दिया।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਚੰਦਨ ਸਿੰਘ ਨੁਗਿਆਲ 17 ਦਸੰਬਰ 1961 ਨੂੰ 6 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਅਤੇ ਯੂਨਿਟ ਦੀ ਸ਼ਾਨਦਾਰ ਅਗਵਾਈ ਕੀਤੀ। ਉਨ੍ਹਾਂ ਨੇ ਫਰਵਰੀ ਤੋਂ ਦਸੰਬਰ 1986 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਕਮਾਂਡ ਸੰਭਾਲੀ। ਬਾਅਦ ਵਿੱਚ ਲੈਫਟੀਨੈਂਟ ਜਨਰਲ ਵਜੋਂ ਪੀਵੀਐਸਐਮ ਅਤੇ ਯੂਵਾਈਐਸਐਮ ਨਾਲ ਸਨਮਾਨਿਤ ਹੋਏ, ਉਨ੍ਹਾਂ ਨੇ ਸੈਂਟਰ ਵਿਖੇ ਸਿਖਲਾਈ ਅਤੇ ਖੇਡਾਂ ਨੂੰ ਉੱਚਾ ਚੁੱਕਿਆ।"
    },
    {
        "art_num": 54,
        "title_en": "Brigadier MML Ahuja, VSM",
        "title_hi": "ब्रिगेडियर एमएमएल आहूजा, वीएसएम",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਐਮਐਮਐਲ ਆਹੂਜਾ, ਵੀਐਸਐਮ",
        "year_en": "December 1986 - May 1988",
        "year_hi": "दिसंबर 1986 - मई 1988",
        "year_pa": "ਦਸੰਬਰ 1986 - ਮਈ 1988",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER MML AHUJA, VSM (December 1986 - May 1988)",
        "header_hi": "ब्रिगेडियर एमएमएल आहूजा, वीएसएम (दिसंबर 1986 - मई 1988)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਐਮਐਮਐਲ ਆਹੂਜਾ, ਵੀਐਸਐਮ (ਦਸੰਬਰ 1986 - ਮਈ 1988)",
        "writeup_en": "Brigadier Madan Mohan Lal Ahuja was commissioned into 5 SIKH on 07 June 1959. He commanded 18 SIKH in Counter Insurgency Operations in Nagaland and held vital staff roles. He commanded the Sikh Regimental Centre from December 1986 to May 1988. Awarded the Vishisht Seva Medal, he spearheaded key construction projects, training ranges, and community welfare institutions at Ramgarh.",
        "writeup_hi": "ब्रिगेडियर मदन मोहन लाल आहूजा 7 जून 1959 को 5 सिख में कमीशन हुए। उन्होंने नागालैंड में 18 सिख की कमान संभाली और महत्वपूर्ण स्टाफ नियुक्तियों पर रहे। उन्होंने दिसंबर 1986 से मई 1988 तक सिख रेजिमेंटल सेंटर की कमान संभाली। विशिष्ट सेवा मेडल से सम्मानित, उन्होंने रामगढ़ में महत्वपूर्ण निर्माण परियोजनाओं, फायरिंग रेंजों और कल्याणकारी संस्थानों का निर्माण कराया।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਮਦਨ ਮੋਹਨ ਲਾਲ ਆਹੂਜਾ 7 ਜੂਨ 1959 ਨੂੰ 5 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ। ਉਨ੍ਹਾਂ ਨੇ ਨਾਗਾਲੈਂਡ ਵਿੱਚ 18 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ। ਉਨ੍ਹਾਂ ਨੇ ਦਸੰਬਰ 1986 ਤੋਂ ਮਈ 1988 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਕਮਾਂਡ ਸੰਭਾਲੀ। ਵਿਸ਼ਿਸ਼ਟ ਸੇਵਾ ਮੈਡਲ ਨਾਲ ਸਨਮਾਨਿਤ, ਉਨ੍ਹਾਂ ਨੇ ਰਾਮਗੜ੍ਹ ਵਿਖੇ ਉਸਾਰੀ ਪ੍ਰੋਜੈਕਟਾਂ ਅਤੇ ਫਾਇਰਿੰਗ ਰੇਂਜਾਂ ਦਾ ਵਿਕਾਸ ਕੀਤਾ।"
    },
    {
        "art_num": 55,
        "title_en": "Brigadier Trilochan Singh, VSM",
        "title_hi": "ब्रिगेडियर त्रिलोचन सिंह, वीएसएम",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਤ੍ਰਿਲੋਚਨ ਸਿੰਘ, ਵੀਐਸਐਮ",
        "year_en": "May 1988 - August 1989",
        "year_hi": "मई 1988 - अगस्त 1989",
        "year_pa": "ਮਈ 1988 - ਅਗਸਤ 1989",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER TRILOCHAN SINGH, VSM (May 1988 - August 1989)",
        "header_hi": "ब्रिगेडियर त्रिलोचन सिंह, वीएसएम (मई 1988 - अगस्त 1989)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਤ੍ਰਿਲੋਚਨ ਸਿੰਘ, ਵੀਐਸਐਮ (ਮਈ 1988 - ਅਗਸਤ 1989)",
        "writeup_en": "Brigadier Trilochan Singh was commissioned into 5 SIKH on 11 June 1961 and joined 7 SIKH on its re-raising. He commanded 19 SIKH and held key staff and instructional appointments. Commanding the Sikh Regimental Centre from May 1988 to August 1989, he earned the Vishisht Seva Medal for transforming training regimes, administrative efficiency, and religious ethos at Ramgarh.",
        "writeup_hi": "ब्रिगेडियर त्रिलोचन सिंह 11 जून 1961 को 5 सिख में कमीशन हुए और 7 सिख के पुनर्गठन पर उसमें शामिल हुए। उन्होंने 19 सिख की कमान संभाली। मई 1988 से अगस्त 1989 तक सिख रेजिमेंटल सेंटर के कमांडेंट के रूप में, उन्हें प्रशिक्षण व्यवस्था, प्रशासनिक दक्षता और रेजिमेंटल मूल्यों को नई ऊंचाई देने के लिए विशिष्ट सेवा मेडल से सम्मानित किया गया।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਤ੍ਰਿਲੋਚਨ ਸਿੰਘ 11 ਜੂਨ 1961 ਨੂੰ 5 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਅਤੇ ਬਾਅਦ ਵਿੱਚ 19 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ। ਉਨ੍ਹਾਂ ਨੇ ਮਈ 1988 ਤੋਂ ਅਗਸਤ 1989 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਕਮਾਂਡ ਸੰਭਾਲੀ। ਵਿਸ਼ਿਸ਼ਟ ਸੇਵਾ ਮੈਡਲ ਨਾਲ ਸਨਮਾਨਿਤ, ਉਨ੍ਹਾਂ ਨੇ ਰਾਮਗੜ੍ਹ ਵਿਖੇ ਸਿਖਲਾਈ ਅਤੇ ਰੈਜੀਮੈਂਟਲ ਕਦਰਾਂ-ਕੀਮਤਾਂ ਨੂੰ ਮਜ਼ਬੂਤ ਕੀਤਾ।"
    },
    {
        "art_num": 56,
        "title_en": "Brigadier Keshav Singh, AVSM",
        "title_hi": "ब्रिगेडियर केशव सिंह, एवीएसएम",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਕੇਸ਼ਵ ਸਿੰਘ, ਏਵੀਐਸਐਮ",
        "year_en": "August 1989 - August 1990",
        "year_hi": "अगस्त 1989 - अगस्त 1990",
        "year_pa": "ਅਗਸਤ 1989 - ਅਗਸਤ 1990",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER KESHAV SINGH, AVSM (August 1989 - August 1990)",
        "header_hi": "ब्रिगेडियर केशव सिंह, एवीएसएम (अगस्त 1989 - अगस्त 1990)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਕੇਸ਼ਵ ਸਿੰਘ, ਏਵੀਐਸਐਮ (ਅਗਸਤ 1989 - ਅਗਸਤ 1990)",
        "writeup_en": "Brigadier Keshav Singh was commissioned into 2 SIKH on 09 February 1964. He fought with distinction in the 1965 War during the capture of Raja Picquet and commanded 2 SIKH in Counter Insurgency Operations in Mizoram. He commanded the Sikh Regimental Centre from August 1989 to August 1990, earning the Ati Vishisht Seva Medal for exemplary leadership and soldier welfare.",
        "writeup_hi": "ब्रिगेडियर केशव सिंह 9 फरवरी 1964 को 2 सिख में कमीशन हुए। उन्होंने 1965 के युद्ध में राजा पिकेट पर कब्जे के दौरान वीरता से लड़ाई लड़ी और मिजोरम में 2 सिख की कमान संभाली। उन्होंने अगस्त 1989 से अगस्त 1990 तक सिख रेजिमेंटल सेंटर की कमान संभाली और अनुकरणीय नेतृत्व तथा सैनिक कल्याण के लिए अति विशिष्ट सेवा मेडल से सम्मानित हुए।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਕੇਸ਼ਵ ਸਿੰਘ 9 ਫਰਵਰੀ 1964 ਨੂੰ 2 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ। ਉਨ੍ਹਾਂ ਨੇ 1965 ਦੀ ਜੰਗ ਵਿੱਚ ਰਾਜਾ ਪਿਕੇਟ 'ਤੇ ਕਬਜ਼ੇ ਦੌਰਾਨ ਬਹਾਦਰੀ ਦਿਖਾਈ ਅਤੇ ਮਿਜ਼ੋਰਮ ਵਿੱਚ 2 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ। ਉਨ੍ਹਾਂ ਨੇ ਅਗਸਤ 1989 ਤੋਂ ਅਗਸਤ 1990 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਕਮਾਂਡ ਕੀਤੀ ਅਤੇ ਅਤੀ ਵਿਸ਼ਿਸ਼ਟ ਸੇਵਾ ਮੈਡਲ ਪ੍ਰਾਪਤ ਕੀਤਾ।"
    },
    {
        "art_num": 57,
        "title_en": "Colonel SS Chahal",
        "title_hi": "कर्नल एसएस चहल",
        "title_pa": "ਕਰਨਲ ਐਸਐਸ ਚਹਿਲ",
        "year_en": "September 1990 - June 1991",
        "year_hi": "सितंबर 1990 - जून 1991",
        "year_pa": "ਸਤੰਬਰ 1990 - ਜੂਨ 1991",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "COLONEL SS CHAHAL (September 1990 - June 1991)",
        "header_hi": "कर्नल एसएस चहल (सितंबर 1990 - जून 1991)",
        "header_pa": "ਕਰਨਲ ਐਸਐਸ ਚਹਿਲ (ਸਤੰਬਰ 1990 - ਜੂਨ 1991)",
        "writeup_en": "Colonel Sarvjit Singh Chahal was commissioned into 1 SIKH on 27 June 1965, seeing intense combat in the 1965 War and during the 1971 Liberation War on the Eastern Front. He commanded 1 SIKH in Counter Insurgency Operations and led the Sikh Regimental Centre from September 1990 to June 1991, instilling high professional standards, physical endurance, and regimental pride among recruits.",
        "writeup_hi": "कर्नल सर्वजीत सिंह चहल 27 जून 1965 को 1 सिख में कमीशन हुए और उन्होंने 1965 के युद्ध तथा 1971 के बांग्लादेश मुक्ति युद्ध में पूर्वी मोर्चे पर वीरता से भाग लिया। उन्होंने उग्रवाद-विरोधी अभियानों में 1 सिख की कमान संभाली और सितंबर 1990 से जून 1991 तक सिख रेजिमेंटल सेंटर का नेतृत्व करते हुए जवानों में उच्च पेशेवर मानकों और रेजिमेंटल गौरव का संचार किया।",
        "writeup_pa": "ਕਰਨਲ ਸਰਵਜੀਤ ਸਿੰਘ ਚਹਿਲ 27 ਜੂਨ 1965 ਨੂੰ 1 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਅਤੇ 1965 ਤੇ 1971 ਦੀਆਂ ਜੰਗਾਂ ਵਿੱਚ ਹਿੱਸਾ ਲਿਆ। ਉਨ੍ਹਾਂ ਨੇ 1 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ ਅਤੇ ਸਤੰਬਰ 1990 ਤੋਂ ਜੂਨ 1991 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਅਗਵਾਈ ਕਰਦਿਆਂ ਰੰਗਰੂਟਾਂ ਵਿੱਚ ਉੱਚ ਪੇਸ਼ੇਵਰ ਮਿਆਰ ਅਤੇ ਰੈਜੀਮੈਂਟਲ ਮਾਣ ਭਰਿਆ।"
    },
    {
        "art_num": 58,
        "title_en": "Brigadier Kanwaljit Singh",
        "title_hi": "ब्रिगेडियर कंवलजीत सिंह",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਕੰਵਲਜੀਤ ਸਿੰਘ",
        "year_en": "June 1991 - November 1994",
        "year_hi": "जून 1991 - नवंबर 1994",
        "year_pa": "ਜੂਨ 1991 - ਨਵੰਬਰ 1994",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER KANWALJIT SINGH (June 1991 - November 1994)",
        "header_hi": "ब्रिगेडियर कंवलजीत सिंह (जून 1991 - नवंबर 1994)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਕੰਵਲਜੀਤ ਸਿੰਘ (ਜੂਨ 1991 - ਨਵੰਬਰ 1994)",
        "writeup_en": "Brigadier Kanwaljit Singh was commissioned into 4 SIKH on 11 December 1962, joining the unit right after the Battle of Walong. He commanded 4 SIKH in Counter Insurgency Operations and commanded the Sikh Regimental Centre from June 1991 to November 1994. His tenure was highlighted by modernizing training methodologies, organizing grand regimental reunions, and enhancing recruit welfare amenities at Ramgarh.",
        "writeup_hi": "ब्रिगेडियर कंवलजीत सिंह 11 दिसंबर 1962 को 4 सिख में कमीशन हुए और वालोंग की लड़ाई के तुरंत बाद यूनिट में शामिल हुए। उन्होंने 4 सिख की कमान संभाली और जून 1991 से नवंबर 1994 तक सिख रेजिमेंटल सेंटर के कमांडेंट रहे। उनके कार्यकाल में आधुनिक प्रशिक्षण पद्धतियां लागू की गईं, भव्य रेजिमेंटल रीयूनियन आयोजित हुए और जवानों के कल्याण में उल्लेखनीय वृद्धि हुई।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਕੰਵਲਜੀਤ ਸਿੰਘ 11 ਦਸੰਬਰ 1962 ਨੂੰ 4 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ। ਉਨ੍ਹਾਂ ਨੇ 4 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ ਅਤੇ ਜੂਨ 1991 ਤੋਂ ਨਵੰਬਰ 1994 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੇ ਕਮਾਂਡੈਂਟ ਰਹੇ। ਉਨ੍ਹਾਂ ਦੇ ਕਾਰਜਕਾਲ ਵਿੱਚ ਸਿਖਲਾਈ ਤਰੀਕਿਆਂ ਦਾ ਆਧੁਨਿਕੀਕਰਨ ਹੋਇਆ ਅਤੇ ਰਾਮਗੜ੍ਹ ਵਿਖੇ ਜਵਾਨਾਂ ਦੀ ਭਲਾਈ ਲਈ ਕਈ ਕਾਰਜ ਕੀਤੇ ਗਏ।"
    },
    {
        "art_num": 59,
        "title_en": "Colonel Tarlochan Singh Kalra",
        "title_hi": "कर्नल तरलोचन सिंह कालरा",
        "title_pa": "ਕਰਨਲ ਤਰਲੋਚਨ ਸਿੰਘ ਕਾਲਰਾ",
        "year_en": "November 1994 - March 1997",
        "year_hi": "नवंबर 1994 - मार्च 1997",
        "year_pa": "ਨਵੰਬਰ 1994 - ਮਾਰਚ 1997",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "COLONEL TARLOCHAN SINGH KALRA (November 1994 - March 1997)",
        "header_hi": "कर्नल तरलोचन सिंह कालरा (नवंबर 1994 - मार्च 1997)",
        "header_pa": "ਕਰਨਲ ਤਰਲੋਚਨ ਸਿੰਘ ਕਾਲਰਾ (ਨਵੰਬਰ 1994 - ਮਾਰਚ 1997)",
        "writeup_en": "Colonel Tarlochan Singh Kalra was commissioned into 2 SIKH on 15 June 1966 and served in the 1971 War in Jammu and Kashmir. He commanded 2 SIKH during Operation Meghdoot on the Siachen Glacier. He commanded the Sikh Regimental Centre from November 1994 to March 1997, conceptualizing the Virasat Museum, establishing the Regimental War Memorial, and instituting comprehensive sports development programs.",
        "writeup_hi": "कर्नल तरलोचन सिंह कालरा 15 जून 1966 को 2 सिख में कमीशन हुए और 1971 के युद्ध में भाग लिया। उन्होंने सियाचिन ग्लेशियर पर ऑपरेशन मेघदूत के दौरान 2 सिख की कमान संभाली। उन्होंने नवंबर 1994 से मार्च 1997 तक सिख रेजिमेंटल सेंटर की कमान संभाली, विरासत संग्रहालय की अवधारणा तैयार की, रेजिमेंटल युद्ध स्मारक की स्थापना की और व्यापक खेल विकास कार्यक्रमों की शुरुआत की।",
        "writeup_pa": "ਕਰਨਲ ਤਰਲੋਚਨ ਸਿੰਘ ਕਾਲਰਾ 15 ਜੂਨ 1966 ਨੂੰ 2 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਅਤੇ 1971 ਦੀ ਜੰਗ ਵਿੱਚ ਹਿੱਸਾ ਲਿਆ। ਉਨ੍ਹਾਂ ਨੇ ਸਿਆਚਿਨ ਗਲੇਸ਼ੀਅਰ 'ਤੇ ਆਪ੍ਰੇਸ਼ਨ ਮੇਘਦੂਤ ਦੌਰਾਨ 2 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ। ਉਨ੍ਹਾਂ ਨੇ ਨਵੰਬਰ 1994 ਤੋਂ ਮਾਰਚ 1997 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਕਮਾਂਡ ਕੀਤੀ, ਵਿਰਾਸਤ ਅਜਾਇਬ ਘਰ ਦੀ ਕਲਪਨਾ ਕੀਤੀ ਅਤੇ ਰੈਜੀਮੈਂਟਲ ਯੁੱਧ ਸਮਾਰਕ ਸਥਾਪਿਤ ਕੀਤਾ।"
    },
    {
        "art_num": 60,
        "title_en": "Colonel HS Toor",
        "title_hi": "कर्नल एचएस तूर",
        "title_pa": "ਕਰਨਲ ਐਚਐਸ ਤੂਰ",
        "year_en": "April 1997 - April 1998",
        "year_hi": "अप्रैल 1997 - अप्रैल 1998",
        "year_pa": "ਅਪ੍ਰੈਲ 1997 - ਅਪ੍ਰੈਲ 1998",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "COLONEL HS TOOR (April 1997 - April 1998)",
        "header_hi": "कर्नल एचएस तूर (अप्रैल 1997 - अप्रैल 1998)",
        "header_pa": "ਕਰਨਲ ਐਚਐਸ ਤੂਰ (ਅਪ੍ਰੈਲ 1997 - ਅਪ੍ਰੈਲ 1998)",
        "writeup_en": "Colonel Harnek Singh Toor was commissioned into 18 SIKH on 14 March 1971 and served in the 1971 War on the Western Front. He commanded 18 SIKH at Bikaner and led the Sikh Regimental Centre as Commandant from April 1997 to April 1998. He spearheaded the 150th Sesquicentennial Celebrations of the Sikh Regiment, elevating regimental pride, infrastructure modernization, and soldier training standards.",
        "writeup_hi": "कर्नल हरनेक सिंह तूर 14 मार्च 1971 को 18 सिख में कमीशन हुए और 1971 के युद्ध में पश्चिमी मोर्चे पर सेवा दी। उन्होंने बीकानेर में 18 सिख की कमान संभाली और अप्रैल 1997 से अप्रैल 1998 तक सिख रेजिमेंटल सेंटर के कमांडेंट रहे। उन्होंने सिख रेजिमेंट के 150वें स्थापना वर्ष समारोह (सेसक्विशताब्दी) का शानदार नेतृत्व किया और सेंटर के आधुनिकीकरण को गति दी।",
        "writeup_pa": "ਕਰਨਲ ਹਰਨੇਕ ਸਿੰਘ ਤੂਰ 14 ਮਾਰਚ 1971 ਨੂੰ 18 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਅਤੇ 1971 ਦੀ ਜੰਗ ਵਿੱਚ ਹਿੱਸਾ ਲਿਆ। ਉਨ੍ਹਾਂ ਨੇ 18 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ ਅਤੇ ਅਪ੍ਰੈਲ 1997 ਤੋਂ ਅਪ੍ਰੈਲ 1998 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੇ ਕਮਾਂਡੈਂਟ ਰਹੇ। ਉਨ੍ਹਾਂ ਨੇ ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦੇ 150ਵੇਂ ਸਥਾਪਨਾ ਦਿਵਸ ਸਮਾਗਮਾਂ ਦੀ ਸਫਲ ਅਗਵਾਈ ਕੀਤੀ।"
    },
    {
        "art_num": 61,
        "title_en": "Brigadier Rajinder Sharma",
        "title_hi": "ब्रिगेडियर राजिंदर शर्मा",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਰਾਜਿੰਦਰ ਸ਼ਰਮਾ",
        "year_en": "May 1998 - December 2001",
        "year_hi": "मई 1998 - दिसंबर 2001",
        "year_pa": "ਮਈ 1998 - ਦਸੰਬਰ 2001",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER RAJINDER SHARMA (May 1998 - December 2001)",
        "header_hi": "ब्रिगेडियर राजिंदर शर्मा (मई 1998 - दिसंबर 2001)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਰਾਜਿੰਦਰ ਸ਼ਰਮਾ (ਮਈ 1998 - ਦਸੰਬਰ 2001)",
        "writeup_en": "Brigadier Rajinder Sharma was commissioned into 17 SIKH on 21 December 1968 and commanded the Battalion in Counter Insurgency Operations. He commanded the Sikh Regimental Centre from May 1998 to December 2001, providing exemplary leadership during the 1999 Kargil Conflict. He oversaw mobilization, war reinforcement training, and family welfare support, ensuring the Regiment achieved glorious battle honours during Kargil.",
        "writeup_hi": "ब्रिगेडियर राजिंदर शर्मा 21 दिसंबर 1968 को 17 सिख में कमीशन हुए और उग्रवाद-विरोधी अभियानों में बटालियन की कमान संभाली। उन्होंने मई 1998 से दिसंबर 2001 तक सिख रेजिमेंटल सेंटर की कमान संभाली और 1999 के कारगिल युद्ध के दौरान अनुकरणीय नेतृत्व प्रदान किया। उन्होंने युद्ध सुदृढीकरण, कठिन प्रशिक्षण और सैनिक परिवारों के कल्याण का उत्कृष्ट प्रबंधन किया।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਰਾਜਿੰਦਰ ਸ਼ਰਮਾ 21 ਦਸੰਬਰ 1968 ਨੂੰ 17 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਅਤੇ ਬਟਾਲੀਅਨ ਦੀ ਕਮਾਂਡ ਕੀਤੀ। ਉਨ੍ਹਾਂ ਨੇ ਮਈ 1998 ਤੋਂ ਦਸੰਬਰ 2001 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਕਮਾਂਡ ਸੰਭਾਲੀ ਅਤੇ 1999 ਦੀ ਕਾਰਗਿਲ ਜੰਗ ਦੌਰਾਨ ਸ਼ਾਨਦਾਰ ਅਗਵਾਈ ਕੀਤੀ ਅਤੇ ਜੰਗੀ ਸਿਖਲਾਈ ਤੇ ਪਰਿਵਾਰਕ ਭਲਾਈ ਨੂੰ ਮਜ਼ਬੂਤ ਕੀਤਾ।"
    },
    {
        "art_num": 62,
        "title_en": "Brigadier APS Pakianathan, VSM**",
        "title_hi": "ब्रिगेडियर एपीएस पाकियानाथन, वीएसएम**",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਏਪੀਐਸ ਪਾਕੀਆਨਾਥਨ, ਵੀਐਸਐਮ**",
        "year_en": "December 2001 - October 2002",
        "year_hi": "दिसंबर 2001 - अक्टूबर 2002",
        "year_pa": "ਦਸੰਬਰ 2001 - ਅਕਤੂਬਰ 2002",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER APS PAKIANATHAN, VSM** (December 2001 - October 2002)",
        "header_hi": "ब्रिगेडियर एपीएस पाकियानाथन, वीएसएम** (दिसंबर 2001 - अक्टूबर 2002)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਏਪੀਐਸ ਪਾਕੀਆਨਾਥਨ, ਵੀਐਸਐਮ** (ਦਸੰਬਰ 2001 - ਅਕਤੂਬਰ 2002)",
        "writeup_en": "Brigadier Albert Philip Samuel Pakianathan was commissioned into 17 SIKH in August 1976. Awarded the Vishisht Seva Medal twice, he held prominent staff and instructional appointments at the College of Combat. He commanded the Sikh Regimental Centre from December 2001 to October 2002 during Operation Parakram, enhancing physical conditioning, tactical proficiency, and training infrastructure at Ramgarh.",
        "writeup_hi": "ब्रिगेडियर अल्बर्ट फिलिप सैमुअल पाकियानाथन अगस्त 1976 में 17 सिख में कमीशन हुए। दो बार विशिष्ट सेवा मेडल से सम्मानित, उन्होंने महत्वपूर्ण स्टाफ और अनुदेशक नियुक्तियां निभाईं। उन्होंने दिसंबर 2001 से अक्टूबर 2002 तक ऑपरेशन पराक्रम के दौरान सिख रेजिमेंटल सेंटर की कमान संभाली और सामरिक दक्षता, शारीरिक क्षमता तथा प्रशिक्षण सुविधाओं को नई ऊंचाई दी।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਐਲਬਰਟ ਫਿਲਿਪ ਸੈਮੂਅਲ ਪਾਕੀਆਨਾਥਨ ਅਗਸਤ 1976 ਵਿੱਚ 17 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ। ਦੋ ਵਾਰ ਵਿਸ਼ਿਸ਼ਟ ਸੇਵਾ ਮੈਡਲ ਨਾਲ ਸਨਮਾਨਿਤ, ਉਨ੍ਹਾਂ ਨੇ ਦਸੰਬਰ 2001 ਤੋਂ ਅਕਤੂਬਰ 2002 ਤੱਕ ਆਪ੍ਰੇਸ਼ਨ ਪਰਾਕ੍ਰਮ ਦੌਰਾਨ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਕਮਾਂਡ ਕੀਤੀ ਅਤੇ ਸਿਖਲਾਈ ਢਾਂਚੇ ਨੂੰ ਬਹੁਤ ਮਜ਼ਬੂਤ ਕੀਤਾ।"
    },
    {
        "art_num": 63,
        "title_en": "Brigadier RK Gupta, VSM",
        "title_hi": "ब्रिगेडियर आरके गुप्ता, वीएसएम",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਆਰਕੇ ਗੁਪਤਾ, ਵੀਐਸਐਮ",
        "year_en": "October 2002 - June 2004",
        "year_hi": "अक्टूबर 2002 - जून 2004",
        "year_pa": "ਅਕਤੂਬਰ 2002 - ਜੂਨ 2004",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER RK GUPTA, VSM (October 2002 - June 2004)",
        "header_hi": "ब्रिगेडियर आरके गुप्ता, वीएसएम (अक्टूबर 2002 - जून 2004)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਆਰਕੇ ਗੁਪਤਾ, ਵੀਐਸਐਮ (ਅਕਤੂਬਰ 2002 - ਜੂਨ 2004)",
        "writeup_en": "Brigadier Ravi Kant Gupta was commissioned into 10 SIKH in November 1971 and served in the 1971 War in Punjab. He commanded 10 SIKH in intense Counter Insurgency Operations in Jammu and Kashmir. He commanded the Sikh Regimental Centre from October 2002 to June 2004, receiving the Vishisht Seva Medal. He modernized firing ranges, introduced IT in administration, and constructed the iconic Khalsa Dwar.",
        "writeup_hi": "ब्रिगेडियर रवि कांत गुप्ता नवंबर 1971 में 10 सिख में कमीशन हुए और 1971 के युद्ध में भाग लिया। उन्होंने जम्मू-कश्मीर में 10 सिख की कमान संभाली। उन्होंने अक्टूबर 2002 से जून 2004 तक सिख रेजिमेंटल सेंटर की कमान संभाली और विशिष्ट सेवा मेडल प्राप्त किया। उन्होंने आधुनिक फायरिंग रेंज बनाईं, प्रशासन में आईटी लागू किया और प्रसिद्ध खालसा द्वार का निर्माण कराया।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਰਵੀ ਕਾਂਤ ਗੁਪਤਾ ਨਵੰਬਰ 1971 ਵਿੱਚ 10 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਅਤੇ 1971 ਦੀ ਜੰਗ ਵਿੱਚ ਹਿੱਸਾ ਲਿਆ। ਉਨ੍ਹਾਂ ਨੇ ਅਕਤੂਬਰ 2002 ਤੋਂ ਜੂਨ 2004 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਕਮਾਂਡ ਕੀਤੀ ਅਤੇ ਵਿਸ਼ਿਸ਼ਟ ਸੇਵਾ ਮੈਡਲ ਪ੍ਰਾਪਤ ਕੀਤਾ। ਉਨ੍ਹਾਂ ਨੇ ਫਾਇਰਿੰਗ ਰੇਂਜਾਂ ਦਾ ਆਧੁਨਿਕੀਕਰਨ ਕੀਤਾ ਅਤੇ ਇਤਿਹਾਸਕ ਖਾਲਸਾ ਦੁਆਰ ਦੀ ਉਸਾਰੀ ਕਰਵਾਈ।"
    },
    {
        "art_num": 64,
        "title_en": "Brigadier IS Gakhal",
        "title_hi": "ब्रिगेडियर आईएस गखल",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਆਈਐਸ ਗਾਖਲ",
        "year_en": "June 2004 - September 2006",
        "year_hi": "जून 2004 - सितंबर 2006",
        "year_pa": "ਜੂਨ 2004 - ਸਤੰਬਰ 2006",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER IS GAKHAL (June 2004 - September 2006)",
        "header_hi": "ब्रिगेडियर आईएस गखल (जून 2004 - सितंबर 2006)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਆਈਐਸ ਗਾਖਲ (ਜੂਨ 2004 - ਸਤੰਬਰ 2006)",
        "writeup_en": "Brigadier Inderjit Singh Gakhal was commissioned into 1 SIKH in December 1973. A distinguished scholar-soldier and sportsman, he commanded 20 SIKH on the Line of Control and a Rashtriya Rifles Sector in active Counter-Terrorist operations. Commanding the Sikh Regimental Centre from June 2004 to September 2006, he authored extensive historical works, founded the Soldiers' Club and Sainik Parivar Kendra, and revived regimental sports teams.",
        "writeup_hi": "ब्रिगेडियर इंद्रजीत सिंह गखल दिसंबर 1973 में 1 सिख में कमीशन हुए। एक उत्कृष्ट विद्वान-सैनिक और खिलाड़ी, उन्होंने नियंत्रण रेखा पर 20 सिख और राष्ट्रीय राइफल्स सेक्टर की कमान संभाली। जून 2004 से सितंबर 2006 तक सिख रेजिमेंटल सेंटर के कमांडेंट के रूप में, उन्होंने ऐतिहासिक ग्रंथों का प्रकाशन कराया, सैनिक परिवार मनोरंजन केंद्र व सोल्जर्स क्लब की स्थापना की और रेजिमेंटल खेल टीमों को पुनर्जीवित किया।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਇੰਦਰਜੀਤ ਸਿੰਘ ਗਾਖਲ ਦਸੰਬਰ 1973 ਵਿੱਚ 1 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ। ਇੱਕ ਵਿਦਵਾਨ ਯੋਧੇ ਅਤੇ ਖਿਡਾਰੀ ਵਜੋਂ, ਉਨ੍ਹਾਂ ਨੇ ਐਲਓਸੀ 'ਤੇ 20 ਸਿੱਖ ਅਤੇ ਰਾਸ਼ਟਰੀ ਰਾਈਫਲਜ਼ ਸੈਕਟਰ ਦੀ ਕਮਾਂਡ ਕੀਤੀ। ਜੂਨ 2004 ਤੋਂ ਸਤੰਬਰ 2006 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੇ ਕਮਾਂਡੈਂਟ ਵਜੋਂ ਉਨ੍ਹਾਂ ਨੇ ਸੈਨਿਕ ਪਰਿਵਾਰ ਮਨੋਰੰਜਨ ਕੇਂਦਰ ਤੇ ਸੋਲਜਰਜ਼ ਕਲੱਬ ਦੀ ਸਥਾਪਨਾ ਕੀਤੀ ਅਤੇ ਖੇਡ ਟੀਮਾਂ ਨੂੰ ਨਵੀਂ ਜਾਨ ਦਿੱਤੀ।"
    },
    {
        "art_num": 65,
        "title_en": "Brigadier Rakesh Sharma",
        "title_hi": "ब्रिगेडियर राकेश शर्मा",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਰਾਕੇਸ਼ ਸ਼ਰਮਾ",
        "year_en": "September 2006 - March 2009",
        "year_hi": "सितंबर 2006 - मार्च 2009",
        "year_pa": "ਸਤੰਬਰ 2006 - ਮਾਰਚ 2009",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER RAKESH SHARMA (September 2006 - March 2009)",
        "header_hi": "ब्रिगेडियर राकेश शर्मा (सितंबर 2006 - मार्च 2009)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਰਾਕੇਸ਼ ਸ਼ਰਮਾ (ਸਤੰਬਰ 2006 - ਮਾਰਚ 2009)",
        "writeup_en": "Brigadier Rakesh Sharma was commissioned into 3 SIKH on 16 June 1974 and commanded 10 SIKH. He served as Brigade Major in Operation Pawan in Sri Lanka and commanded the Counter Insurgency and Jungle Warfare School, Vairengte. He commanded the Sikh Regimental Centre from September 2006 to March 2009, during which the Centre conducted Ex-Maitree, the first historic Foreign Joint Military Training with the Royal Thailand Army.",
        "writeup_hi": "ब्रिगेडियर राकेश शर्मा 16 जून 1974 को 3 सिख में कमीशन हुए और 10 सिख की कमान संभाली। उन्होंने श्रीलंका में ऑपरेशन पवन के दौरान ब्रिगेड मेजर के रूप में सेवा दी और सीआईजेडब्ल्यू स्कूल, वैरेंगटे के कमांडेंट रहे। सितंबर 2006 से मार्च 2009 तक सिख रेजिमेंटल सेंटर के कमांडेंट के रूप में उनके कार्यकाल में रॉयल थाईलैंड सेना के साथ ऐतिहासिक पहला विदेशी संयुक्त सैन्य अभ्यास 'एक्स-मैत्री' आयोजित किया गया।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਰਾਕੇਸ਼ ਸ਼ਰਮਾ 16 ਜੂਨ 1974 ਨੂੰ 3 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਅਤੇ 10 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ। ਉਨ੍ਹਾਂ ਨੇ ਸ਼੍ਰੀਲੰਕਾ ਵਿੱਚ ਆਪ੍ਰੇਸ਼ਨ ਪਵਨ ਦੌਰਾਨ ਸੇਵਾ ਕੀਤੀ। ਸਤੰਬਰ 2006 ਤੋਂ ਮਾਰਚ 2009 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੇ ਕਮਾਂਡੈਂਟ ਵਜੋਂ ਉਨ੍ਹਾਂ ਦੇ ਕਾਰਜਕਾਲ ਦੌਰਾਨ ਥਾਈਲੈਂਡ ਦੀ ਫੌਜ ਨਾਲ ਪਹਿਲਾ ਵਿਦੇਸ਼ੀ ਸਾਂਝਾ ਸਿਖਲਾਈ ਅਭਿਆਸ 'ਐਕਸ-ਮੈਤਰੀ' ਕਰਵਾਇਆ ਗਿਆ।"
    },
    {
        "art_num": 66,
        "title_en": "Brigadier HN Mhaisalkar",
        "title_hi": "ब्रिगेडियर एचएन म्हैसालकर",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਐਚਐਨ ਮਹੈਸਾਲਕਰ",
        "year_en": "April 2009 - April 2012",
        "year_hi": "अप्रैल 2009 - अप्रैल 2012",
        "year_pa": "ਅਪ੍ਰੈਲ 2009 - ਅਪ੍ਰੈਲ 2012",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER HN MHAISALKAR (April 2009 - April 2012)",
        "header_hi": "ब्रिगेडियर एचएन म्हैसालकर (अप्रैल 2009 - अप्रैल 2012)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਐਚਐਨ ਮਹੈਸਾਲਕਰ (ਅਪ੍ਰੈਲ 2009 - ਅਪ੍ਰੈਲ 2012)",
        "writeup_en": "Brigadier Harshavardhan Narayan Mhaisalkar was commissioned into 17 SIKH on 15 December 1976. He commanded 13 SIKH and raised 46 Rashtriya Rifles Battalion. He held prestigious instructional roles at Mhow, DSSC Wellington, and High Commission of India in the UK. He served as Commandant of the Sikh Regimental Centre from April 2009 to April 2012, significantly improving training facilities, living amenities, and regimental documentation.",
        "writeup_hi": "ब्रिगेडियर हर्षवर्धन नारायण म्हैसालकर 15 दिसंबर 1976 को 17 सिख में कमीशन हुए। उन्होंने 13 सिख की कमान संभाली और 46 राष्ट्रीय राइफल्स की स्थापना की। उन्होंने महू, डीएसएससी वेलिंगटन और ब्रिटेन में भारतीय उच्चायोग में महत्वपूर्ण भूमिकाएं निभाईं। उन्होंने अप्रैल 2009 से अप्रैल 2012 तक सिख रेजिमेंटल सेंटर के कमांडेंट के रूप में सेवा दी और प्रशिक्षण तथा जीवन स्तर में उत्कृष्ट सुधार किए।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਹਰਸ਼ਵਰਧਨ ਨਾਰਾਇਣ ਮਹੈਸਾਲਕਰ 15 ਦਸੰਬਰ 1976 ਨੂੰ 17 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ। ਉਨ੍ਹਾਂ ਨੇ 13 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ ਅਤੇ 46 ਆਰ ਆਰ ਬਟਾਲੀਅਨ ਖੜ੍ਹੀ ਕੀਤੀ। ਅਪ੍ਰੈਲ 2009 ਤੋਂ ਅਪ੍ਰੈਲ 2012 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੇ ਕਮਾਂਡੈਂਟ ਵਜੋਂ ਉਨ੍ਹਾਂ ਨੇ ਸਿਖਲਾਈ ਸਹੂਲਤਾਂ ਅਤੇ ਰੈਜੀਮੈਂਟਲ ਰਿਕਾਰਡਾਂ ਵਿੱਚ ਸ਼ਾਨਦਾਰ ਸੁਧਾਰ ਕੀਤੇ।"
    },
    {
        "art_num": 67,
        "title_en": "Brigadier Pushkar Hiteshi",
        "title_hi": "ब्रिगेडियर पुष्कर हितेषी",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਪੁਸ਼ਕਰ ਹਿਤੇਸ਼ੀ",
        "year_en": "May 2012 - October 2014",
        "year_hi": "मई 2012 - अक्टूबर 2014",
        "year_pa": "ਮਈ 2012 - ਅਕਤੂਬਰ 2014",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER PUSHKAR HITESHI (May 2012 - October 2014)",
        "header_hi": "ब्रिगेडियर पुष्कर हितेषी (मई 2012 - अक्टूबर 2014)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਪੁਸ਼ਕਰ ਹਿਤੇਸ਼ੀ (ਮਈ 2012 - ਅਕਤੂਬਰ 2014)",
        "writeup_en": "Brigadier Pushkar Hiteshi was commissioned into 7 SIKH on 18 June 1983. He commanded 22 SIKH in Operation Rakshak in Jammu and Kashmir and commanded 322 Infantry Brigade. He served as a UN Military Observer in Sierra Leone. As Commandant of the Sikh Regimental Centre from May 2012 to October 2014, he instituted modern tactical training simulations and elevated recruit physical conditioning and regimental discipline.",
        "writeup_hi": "ब्रिगेडियर पुष्कर हितेषी 18 जून 1983 को 7 सिख में कमीशन हुए। उन्होंने जम्मू-कश्मीर में ऑपरेशन रक्षक में 22 सिख और 322 इन्फैंट्री ब्रिगेड की कमान संभाली। उन्होंने सिएरा लियोन में संयुक्त राष्ट्र सैन्य पर्यवेक्षक के रूप में कार्य किया। मई 2012 से अक्टूबर 2014 तक सिख रेजिमेंटल सेंटर के कमांडेंट के रूप में, उन्होंने आधुनिक सामरिक प्रशिक्षण सिमुलेशन और उत्कृष्ट अनुशासन स्थापित किया।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਪੁਸ਼ਕਰ ਹਿਤੇਸ਼ੀ 18 ਜੂਨ 1983 ਨੂੰ 7 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ। ਉਨ੍ਹਾਂ ਨੇ ਜੰਮੂ-ਕਸ਼ਮੀਰ ਵਿੱਚ 22 ਸਿੱਖ ਅਤੇ 322 ਇਨਫੈਂਟਰੀ ਬ੍ਰਿਗੇਡ ਦੀ ਕਮਾਂਡ ਕੀਤੀ। ਮਈ 2012 ਤੋਂ ਅਕਤੂਬਰ 2014 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੇ ਕਮਾਂਡੈਂਟ ਵਜੋਂ ਉਨ੍ਹਾਂ ਨੇ ਆਧੁਨਿਕ ਸਿਖਲਾਈ ਤਕਨੀਕਾਂ ਅਤੇ ਰੈਜੀਮੈਂਟਲ ਅਨੁਸ਼ਾਸਨ ਨੂੰ ਨਵੀਆਂ ਬੁਲੰਦੀਆਂ 'ਤੇ ਪਹੁੰਚਾਇਆ।"
    },
    {
        "art_num": 68,
        "title_en": "Brigadier KBK Keshab",
        "title_hi": "ब्रिगेडियर केबीके केशब",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਕੇਬੀਕੇ ਕੇਸ਼ਬ",
        "year_en": "October 2014 - January 2017",
        "year_hi": "अक्टूबर 2014 - जनवरी 2017",
        "year_pa": "ਅਕਤੂਬਰ 2014 - ਜਨਵਰੀ 2017",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER KBK KESHAB (October 2014 - January 2017)",
        "header_hi": "ब्रिगेडियर केबीके केशब (अक्टूबर 2014 - जनवरी 2017)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਕੇਬੀਕੇ ਕੇਸ਼ਬ (ਅਕਤੂਬਰ 2014 - ਜਨਵਰੀ 2017)",
        "writeup_en": "Brigadier Kul Bhushan Kumar Keshab was commissioned into 18 SIKH in June 1982 and commanded 17 SIKH and 51 Infantry Brigade. A national-level sportsman in tennis and athletics, he commanded the Sikh Regimental Centre from October 2014 to January 2017. Under his leadership, the Centre achieved the GOC-in-C Central Command Unit Citation, won Best Marching Contingent at Republic Day Parade 2015, and earned ISO 9001 certification.",
        "writeup_hi": "ब्रिगेडियर कुल भूषण कुमार केशब जून 1982 में 18 सिख में कमीशन हुए और 17 सिख तथा 51 इन्फैंट्री ब्रिगेड की कमान संभाली। टेनिस और एथलेटिक्स में राष्ट्रीय स्तर के खिलाड़ी, उन्होंने अक्टूबर 2014 से जनवरी 2017 तक सिख रेजिमेंटल सेंटर की कमान संभाली। उनके नेतृत्व में सेंटर ने जीओसी-इन-सी यूनिट प्रशस्ति पत्र जीता, गणतंत्र दिवस परेड 2015 में सर्वश्रेष्ठ मार्चिंग दल का पुरस्कार जीता और आईएसओ 9001 प्रमाणन प्राप्त किया।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਕੁਲ ਭੂਸ਼ਣ ਕੁਮਾਰ ਕੇਸ਼ਬ ਜੂਨ 1982 ਵਿੱਚ 18 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਅਤੇ 17 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ। ਅਕਤੂਬਰ 2014 ਤੋਂ ਜਨਵਰੀ 2017 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੇ ਕਮਾਂਡੈਂਟ ਵਜੋਂ ਉਨ੍ਹਾਂ ਦੀ ਅਗਵਾਈ ਹੇਠ ਸੈਂਟਰ ਨੇ ਸੈਂਟਰਲ ਕਮਾਂਡ ਯੂਨਿਟ ਪ੍ਰਸ਼ੰਸਾ ਪੱਤਰ, ਗਣਤੰਤਰ ਦਿਵਸ ਪਰੇਡ 2015 ਵਿੱਚ ਸਰਵੋਤਮ ਮਾਰਚਿੰਗ ਦਲ ਦਾ ਪੁਰਸਕਾਰ ਅਤੇ ISO 9001 ਪ੍ਰਮਾਣੀਕਰਨ ਹਾਸਲ ਕੀਤਾ।"
    },
    {
        "art_num": 69,
        "title_en": "Brigadier Rakesh Raina, VSM",
        "title_hi": "ब्रिगेडियर राकेश रैना, वीएसएम",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਰਾਕੇਸ਼ ਰੈਨਾ, ਵੀਐਸਐਮ",
        "year_en": "January 2017 - January 2020",
        "year_hi": "जनवरी 2017 - जनवरी 2020",
        "year_pa": "ਜਨਵਰੀ 2017 - ਜਨਵਰੀ 2020",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER RAKESH RAINA, VSM (January 2017 - January 2020)",
        "header_hi": "ब्रिगेडियर राकेश रैना, वीएसएम (जनवरी 2017 - जनवरी 2020)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਰਾਕੇਸ਼ ਰੈਨਾ, वीएसएम (ਜਨਵਰੀ 2017 - ਜਨਵਰੀ 2020)",
        "writeup_en": "Brigadier Rakesh Raina was commissioned into 13 SIKH on 08 June 1985 and commanded 13 SIKH and 67 Infantry Brigade. Awarded the Vishisht Seva Medal and VCOAS Commendation Card, he commanded the Sikh Regimental Centre from January 2017 to January 2020. Under his stewardship, the Sikh Regiment Contingent was adjudged Best Marching Contingent at the Army Day Parade, alongside major modernization of recruit facilities and heritage preservation.",
        "writeup_hi": "ब्रिगेडियर राकेश रैना 8 जून 1985 को 13 सिख में कमीशन हुए और 13 सिख तथा 67 इन्फैंट्री ब्रिगेड की कमान संभाली। विशिष्ट सेवा मेडल और वीसीओएएस प्रशस्ति पत्र से सम्मानित, उन्होंने जनवरी 2017 से जनवरी 2020 तक सिख रेजिमेंटल सेंटर की कमान संभाली। उनके नेतृत्व में सिख रेजिमेंट के मार्चिंग दल को सेना दिवस परेड में सर्वश्रेष्ठ मार्चिंग दल घोषित किया गया तथा रंगरूट सुविधाओं का आधुनिकीकरण हुआ।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਰਾਕੇਸ਼ ਰੈਨਾ 8 ਜੂਨ 1985 ਨੂੰ 13 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਅਤੇ 13 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ। ਵਿਸ਼ਿਸ਼ਟ ਸੇਵਾ ਮੈਡਲ ਨਾਲ ਸਨਮਾਨਿਤ, ਉਨ੍ਹਾਂ ਨੇ ਜਨਵਰੀ 2017 ਤੋਂ ਜਨਵਰੀ 2020 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਕਮਾਂਡ ਸੰਭਾਲੀ। ਉਨ੍ਹਾਂ ਦੀ ਅਗਵਾਈ ਹੇਠ ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦੀ ਟੁਕੜੀ ਨੂੰ ਆਰਮੀ ਡੇ ਪਰੇਡ ਵਿੱਚ ਸਰਵੋਤਮ ਮਾਰਚਿੰਗ ਦਲ ਚੁਣਿਆ ਗਿਆ।"
    },
    {
        "art_num": 70,
        "title_en": "Brigadier M Sri Kumar, SC",
        "title_hi": "ब्रिगेडियर एम श्री कुमार, एससी",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਐਮ ਸ਼੍ਰੀ ਕੁਮਾਰ, ਐਸਸੀ",
        "year_en": "February 2020 - April 2022",
        "year_hi": "फरवरी 2020 - अप्रैल 2022",
        "year_pa": "ਫਰਵਰੀ 2020 - ਅਪ੍ਰੈਲ 2022",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER M SRI KUMAR, SC (February 2020 - April 2022)",
        "header_hi": "ब्रिगेडियर एम श्री कुमार, एससी (फरवरी 2020 - अप्रैल 2022)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਐਮ ਸ਼੍ਰੀ ਕੁਮਾਰ, ਐਸਸੀ (ਫਰਵਰੀ 2020 - ਅਪ੍ਰੈਲ 2022)",
        "writeup_en": "Brigadier M Sri Kumar was commissioned into 7 SIKH on 16 December 1989 and commanded 7 SIKH and 32 Infantry Brigade. Awarded the Shaurya Chakra and VCOAS Commendation Card, he commanded the Sikh Regimental Centre from February 2020 to April 2022. Under his command, the Pipes and Drums Band of the Sikh Regimental Centre secured First Position in the Adjutant General's Band Display Competition for 2021, and training infrastructure was extensively upgraded.",
        "writeup_hi": "ब्रिगेडियर एम श्री कुमार 16 दिसंबर 1989 को 7 सिख में कमीशन हुए और 7 सिख तथा 32 इन्फैंट्री ब्रिगेड की कमान संभाली। शौर्य चक्र और वीसीओएएस प्रशस्ति पत्र से सम्मानित, उन्होंने फरवरी 2020 से अप्रैल 2022 तक सिख रेजिमेंटल सेंटर की कमान संभाली। उनकी कमान में सिख रेजिमेंटल सेंटर के पाइप्स एंड ड्रम्स बैंड ने वर्ष 2021 की एडजुटेंट जनरल बैंड प्रतियोगिता में प्रथम स्थान हासिल किया और प्रशिक्षण ढांचे को अपग्रेड किया गया।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਐਮ ਸ਼੍ਰੀ ਕੁਮਾਰ 16 ਦਸੰਬਰ 1989 ਨੂੰ 7 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਅਤੇ 7 ਸਿੱਖ ਦੀ ਕਮਾਂਡ ਕੀਤੀ। ਸ਼ੌਰਿਆ ਚੱਕਰ ਨਾਲ ਸਨਮਾਨਿਤ, ਉਨ੍ਹਾਂ ਨੇ ਫਰਵਰੀ 2020 ਤੋਂ ਅਪ੍ਰੈਲ 2022 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਕਮਾਂਡ ਸੰਭਾਲੀ। ਉਨ੍ਹਾਂ ਦੀ ਕਮਾਂਡ ਹੇਠ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੇ ਪਾਈਪਸ ਐਂਡ ਡਰੰਮਜ਼ ਬੈਂਡ ਨੇ ਸਾਲ 2021 ਲਈ ਐਡਜੂਟੈਂਟ ਜਨਰਲ ਦੇ ਬੈਂਡ ਮੁਕਾਬਲੇ ਵਿੱਚ ਪਹਿਲਾ ਸਥਾਨ ਹਾਸਲ ਕੀਤਾ।"
    },
    {
        "art_num": 71,
        "title_en": "Brigadier Shailesh Sati",
        "title_hi": "ब्रिगेडियर शैलेश सती",
        "title_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਸ਼ੈਲੇਸ਼ ਸਤੀ",
        "year_en": "June 2022 - May 2024",
        "year_hi": "जून 2022 - मई 2024",
        "year_pa": "ਜੂਨ 2022 - ਮਈ 2024",
        "artist_en": "Historical Figure",
        "artist_hi": "ऐतिहासिक व्यक्तित्व",
        "artist_pa": "ਇਤਿਹਾਸਕ ਸ਼ਖਸੀਅਤ",
        "category_en": "Comdts' Gallery",
        "category_hi": "कमांडेंट्स गैलरी",
        "category_pa": "ਕਮਾਂਡੈਂਟਸ ਗੈਲਰੀ",
        "header_en": "BRIGADIER SHAILESH SATI (June 2022 - May 2024)",
        "header_hi": "ब्रिगेडियर शैलेश सती (जून 2022 - मई 2024)",
        "header_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਸ਼ੈਲੇਸ਼ ਸਤੀ (ਜੂਨ 2022 - ਮਈ 2024)",
        "writeup_en": "Brigadier Shailesh Sati was commissioned into 6 SIKH on 13 June 1992 and commanded 6 SIKH and 92 Infantry Brigade. He served in the UN Mission in Congo and held vital staff roles. He commanded the Sikh Regimental Centre from June 2022 to May 2024. During his command, the Sikh Regiment Marching Contingent was awarded the prestigious Best Marching Contingent Trophy at the Republic Day Parade 2024.",
        "writeup_hi": "ब्रिगेडियर शैलेश सती 13 जून 1992 को 6 सिख में कमीशन हुए और उन्होंने 6 सिख तथा 92 इन्फैंट्री ब्रिगेड की कमान संभाली। उन्होंने कांगो में संयुक्त राष्ट्र मिशन में सेवा दी। उन्होंने जून 2022 से मई 2024 तक सिख रेजिमेंटल सेंटर की कमान संभाली। उनके गौरवशाली नेतृत्व में, सिख रेजिमेंट के मार्चिंग दल को गणतंत्र दिवस परेड 2024 में प्रतिष्ठित सर्वश्रेष्ठ मार्चिंग दल ट्रॉफी से सम्मानित किया गया।",
        "writeup_pa": "ਬ੍ਰਿਗੇਡੀਅਰ ਸ਼ੈਲੇਸ਼ ਸਤੀ 13 ਜੂਨ 1992 ਨੂੰ 6 ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹੋਏ ਅਤੇ ਉਨ੍ਹਾਂ ਨੇ 6 ਸਿੱਖ ਤੇ 92 ਇਨਫੈਂਟਰੀ ਬ੍ਰਿਗੇਡ ਦੀ ਕਮਾਂਡ ਕੀਤੀ। ਉਨ੍ਹਾਂ ਨੇ ਕਾਂਗੋ ਵਿੱਚ ਸੰਯੁਕਤ ਰਾਸ਼ਟਰ ਮਿਸ਼ਨ ਵਿੱਚ ਸੇਵਾ ਨਿਭਾਈ। ਉਨ੍ਹਾਂ ਨੇ ਜੂਨ 2022 ਤੋਂ ਮਈ 2024 ਤੱਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੀ ਕਮਾਂਡ ਸੰਭਾਲੀ। ਉਨ੍ਹਾਂ ਦੀ ਅਗਵਾਈ ਹੇਠ ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦੇ ਮਾਰਚਿੰਗ ਦਲ ਨੂੰ ਗਣਤੰਤਰ ਦਿਵਸ ਪਰੇਡ 2024 ਵਿੱਚ ਸਰਵੋਤਮ ਮਾਰਚਿੰਗ ਦਲ ਟਰਾਫੀ ਨਾਲ ਸਨਮਾਨਿਤ ਕੀਤਾ ਗਿਆ।"
    }
]

def generate_html_page(item, lang, prev_num, next_num, total_pieces=32, piece_index=1):
    art_num = item["art_num"]
    
    if lang == 'en':
        filename = f"art{art_num}.html"
        title = item["title_en"]
        site_title = f"{title} - Museum Gallery"
        home_url = "index_en.html"
        home_text = "Back to Home"
        audio_src = f"assets/audio/audio_{art_num}.mp3"
        listen_text = "Listen to Narration"
        pause_text = "Pause Audio"
        meta_title_lbl = "Title:"
        meta_cat_lbl = "Category:"
        meta_artist_lbl = "Artist:"
        meta_year_lbl = "Year:"
        cat_val = item["category_en"]
        artist_val = item["artist_en"]
        year_val = item["year_en"]
        header_text = item["header_en"]
        writeup_text = item["writeup_en"]
        prev_url = f"art{prev_num}.html" if prev_num else "#"
        next_url = f"art{next_num}.html" if next_num else "#"
        prev_text = "Previous Piece"
        next_text = "Next Piece"
        piece_counter = f"Piece {piece_index} / {total_pieces}"
        qr_title = "Open on Mobile"
        qr_desc = "Scan to view this art record in Chrome on your phone."
        portal_label = "🏛️ Language Portal"
    elif lang == 'hi':
        filename = f"art{art_num}_hi.html"
        title = item["title_hi"]
        site_title = f"{title} - विरासत संग्रहालय"
        home_url = "index_hi.html"
        home_text = "मुख्य पृष्ठ"
        audio_src = f"assets/audio_hi/audio_{art_num}.mp3"
        listen_text = "वर्णन सुनें"
        pause_text = "ऑडियो रोकें"
        meta_title_lbl = "शीर्षक:"
        meta_cat_lbl = "श्रेणी:"
        meta_artist_lbl = "कलाकार:"
        meta_year_lbl = "वर्ष:"
        cat_val = item["category_hi"]
        artist_val = item["artist_hi"]
        year_val = item["year_hi"]
        header_text = item["header_hi"]
        writeup_text = item["writeup_hi"]
        prev_url = f"art{prev_num}_hi.html" if prev_num else "#"
        next_url = f"art{next_num}_hi.html" if next_num else "#"
        prev_text = "पिछली कलाकृति"
        next_text = "अगली कलाकृति"
        piece_counter = f"कलाकृति {piece_index} / {total_pieces}"
        qr_title = "मोबाइल पर खोलें"
        qr_desc = "अपने फोन पर इस कलाकृति को देखने के लिए स्कैन करें।"
        portal_label = "🏛️ भाषा चयन"
    else: # pa
        filename = f"art{art_num}_pa.html"
        title = item["title_pa"]
        site_title = f"{title} - ਵਿਰਾਸਤ ਅਜਾਇਬ ਘਰ"
        home_url = "index_pa.html"
        home_text = "ਮੁੱਖ ਪੰਨਾ"
        audio_src = f"assets/audio_pa/audio_{art_num}.mp3"
        listen_text = "ਵੇਰਵਾ ਸੁਣੋ"
        pause_text = "ਆਡੀਓ ਰੋਕੋ"
        meta_title_lbl = "ਸਿਰਲੇਖ:"
        meta_cat_lbl = "ਸ਼੍ਰੇਣੀ:"
        meta_artist_lbl = "ਕਲਾਕਾਰ:"
        meta_year_lbl = "ਸਾਲ:"
        cat_val = item["category_pa"]
        artist_val = item["artist_pa"]
        year_val = item["year_pa"]
        header_text = item["header_pa"]
        writeup_text = item["writeup_pa"]
        prev_url = f"art{prev_num}_pa.html" if prev_num else "#"
        next_url = f"art{next_num}_pa.html" if next_num else "#"
        prev_text = "ਪਿਛਲੀ ਕਲਾਕ੍ਰਿਤੀ"
        next_text = "ਅਗਲੀ ਕਲਾਕ੍ਰਿਤੀ"
        piece_counter = f"ਕਲਾਕ੍ਰਿਤੀ {piece_index} / {total_pieces}"
        qr_title = "ਮੋਬਾਈਲ 'ਤੇ ਖੋਲ੍ਹੋ"
        qr_desc = "ਆਪਣੇ ਫ਼ੋਨ 'ਤੇ ਇਸ ਕਲਾ ਰਿਕਾਰਡ ਨੂੰ ਦੇਖਣ ਲਈ ਸਕੈਨ ਕਰੋ।"
        portal_label = "🏛️ ਭਾਸ਼ਾ ਚੋਣ"

    en_active = 'style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24;"' if lang == 'en' else 'style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;"'
    hi_active = 'style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24;"' if lang == 'hi' else 'style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;"'
    pa_active = 'style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24;"' if lang == 'pa' else 'style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;"'

    prev_disabled = "disabled" if not prev_num else ""
    next_disabled = "disabled" if not next_num else ""

    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{site_title}</title>
<link href="css/style.css" rel="stylesheet"/>
</head>
<body class="portrait-page">
<div class="gallery-container">
<!-- Language Switcher Bar -->
<div class="lang-switch-bar" style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.85); padding: 8px 16px; border-radius: 14px; border: 1px solid var(--glass-border); margin-bottom: 20px; backdrop-filter: blur(12px);">
<a class="nav-link" href="index.html" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.4); color: #cbd5e1;">
    {portal_label}
</a>
<div style="display: flex; gap: 8px; align-items: center;">
<a class="nav-link" href="art{art_num}.html" {en_active}>🇬🇧 English</a>
<a class="nav-link" href="art{art_num}_hi.html" {hi_active}>🇮🇳 हिन्दी</a>
<a class="nav-link" href="art{art_num}_pa.html" {pa_active}>ੴ ਪੰਜਾਬੀ</a>
</div>
</div>

<!-- Home Button -->
<div style="margin-bottom: 20px;">
<a class="nav-link" href="{home_url}" style="display: inline-flex; background: rgba(0,0,0,0.3); padding: 10px 20px; border-radius: 20px; border: 1px solid var(--glass-border);">
<svg fill="none" height="20" stroke="currentColor" stroke-width="2" style="margin-right: 8px;" viewbox="0 0 24 24" width="20">
<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
<polyline points="9 22 9 12 15 12 15 22"></polyline>
</svg> {home_text}</a>
</div>

<h1>{title}</h1>
<div class="photo-wrapper">
<img alt="" class="photo-background" onerror="this.style.display='none'" src="assets/art/art_{art_num}.webp"/>
<img alt="{item['title_en']}" class="photo-main" onerror="this.src='https://placehold.co/1000x600/1e293b/f59e0b?text=Place+Art+Photo+Here'" src="assets/art/art_{art_num}.webp"/>
</div>

<div class="audio-section">
<audio autoplay="" id="artAudio" src="{audio_src}"></audio>
<button class="play-btn" onclick="toggleAudio()">
<svg fill="currentColor" viewbox="0 0 24 24">
<path d="M8 5v14l11-7z"></path>
</svg>
    {listen_text}
</button>
</div>

<div class="description-box">
<strong>{meta_title_lbl}</strong> {title}<br/>
<strong>{meta_cat_lbl}</strong> {cat_val}<br/>
<strong>{meta_artist_lbl}</strong> {artist_val}<br/>
<strong>{meta_year_lbl}</strong> {year_val}
</div>

<div class="description-box">
<strong>{header_text}</strong><br/><br/>
{writeup_text}
</div>

<div class="navigation">
<a class="nav-link {prev_disabled}" href="{prev_url}">
<svg fill="none" height="20" stroke="currentColor" stroke-width="2" viewbox="0 0 24 24" width="20">
<path d="M19 12H5M12 19l-7-7 7-7"></path>
</svg>
    {prev_text}
</a>
<span style="color: #94a3b8;">{piece_counter}</span>
<a class="nav-link {next_disabled}" href="{next_url}">
    {next_text}
<svg fill="none" height="20" stroke="currentColor" stroke-width="2" viewbox="0 0 24 24" width="20">
<path d="M5 12h14M12 5l7 7-7 7"></path>
</svg>
</a>
</div>

<!-- QR Code Section -->
<div class="qr-container">
<div class="qr-wrapper">
<img alt="Scan for mobile" src="assets/qrcodes/qr_art_{art_num}.png"/>
<div class="qr-info">
<h3>{qr_title}</h3>
<p>{qr_desc}</p>
</div>
</div>
</div>

</div>

<script>
    document.addEventListener("DOMContentLoaded", function() {{
        const audio = document.getElementById('artAudio');
        const btn = document.querySelector('.play-btn');

        audio.addEventListener('play', function() {{
            btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg> {pause_text}`;
        }});

        audio.addEventListener('pause', function() {{
            btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg> {listen_text}`;
        }});

        audio.addEventListener('ended', function() {{
            btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg> {listen_text}`;
        }});
        
        // Attempt autoplay
        let playPromise = audio.play();
        if (playPromise !== undefined) {{
            playPromise.catch(error => {{
                console.log("Autoplay prevented by browser:", error);
                const startAudioOnInteract = () => {{
                    audio.play();
                    document.body.removeEventListener('click', startAudioOnInteract);
                    document.body.removeEventListener('touchstart', startAudioOnInteract);
                }};
                document.body.addEventListener('click', startAudioOnInteract);
                document.body.addEventListener('touchstart', startAudioOnInteract);
            }});
        }}
    }});

    function toggleAudio() {{
        const audio = document.getElementById('artAudio');
        if (audio.paused) {{
            audio.play();
        }} else {{
            audio.pause();
        }}
    }}
</script>
</body>
</html>
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

def update_index_dropdowns():
    print("Updating dropdown links in index_en.html, index_hi.html, index_pa.html...", flush=True)
    
    # 1. index_en.html
    with open("index_en.html", "r", encoding="utf-8") as f:
        soup_en = BeautifulSoup(f.read(), "html.parser")
    
    drop_en = soup_en.find("div", id="dropdown-4")
    if drop_en:
        drop_en.clear()
        for item in COMDTS_DATA:
            a_tag = soup_en.new_tag("a", href=f"art{item['art_num']}.html")
            a_tag.string = item["title_en"]
            drop_en.append(a_tag)
            drop_en.append("\n")
    with open("index_en.html", "w", encoding="utf-8") as f:
        f.write(str(soup_en))

    # 2. index_hi.html
    with open("index_hi.html", "r", encoding="utf-8") as f:
        soup_hi = BeautifulSoup(f.read(), "html.parser")
    
    drop_hi = soup_hi.find("div", id="dropdown-4")
    if drop_hi:
        drop_hi.clear()
        for item in COMDTS_DATA:
            a_tag = soup_hi.new_tag("a", href=f"art{item['art_num']}_hi.html")
            a_tag.string = item["title_hi"]
            drop_hi.append(a_tag)
            drop_hi.append("\n")
    with open("index_hi.html", "w", encoding="utf-8") as f:
        f.write(str(soup_hi))

    # 3. index_pa.html
    with open("index_pa.html", "r", encoding="utf-8") as f:
        soup_pa = BeautifulSoup(f.read(), "html.parser")
    
    drop_pa = soup_pa.find("div", id="dropdown-4")
    if drop_pa:
        drop_pa.clear()
        for item in COMDTS_DATA:
            a_tag = soup_pa.new_tag("a", href=f"art{item['art_num']}_pa.html")
            a_tag.string = item["title_pa"]
            drop_pa.append(a_tag)
            drop_pa.append("\n")
    with open("index_pa.html", "w", encoding="utf-8") as f:
        f.write(str(soup_pa))

async def synthesize_audio_recitations():
    print("Generating smart 100-word audio recitations in English, Hindi, and Punjabi...", flush=True)
    os.makedirs("assets/audio", exist_ok=True)
    os.makedirs("assets/audio_hi", exist_ok=True)
    os.makedirs("assets/audio_pa", exist_ok=True)
    
    sem = asyncio.Semaphore(6)

    async def gen_en(art_num, text, title):
        speech_text = f"{title}. {text}"
        p = f"assets/audio/audio_{art_num}.mp3"
        async with sem:
            try:
                comm = edge_tts.Communicate(speech_text, 'en-IN-PrabhatNeural')
                await comm.save(p)
            except Exception as e:
                print(f"Fallback gTTS for EN art{art_num}: {e}")
                tts = gTTS(speech_text, lang='en')
                tts.save(p)

    async def gen_hi(art_num, text, title):
        speech_text = f"{title}. {text}"
        p = f"assets/audio_hi/audio_{art_num}.mp3"
        async with sem:
            try:
                comm = edge_tts.Communicate(speech_text, 'hi-IN-MadhurNeural')
                await comm.save(p)
            except Exception as e:
                print(f"Fallback gTTS for HI art{art_num}: {e}")
                tts = gTTS(speech_text, lang='hi')
                tts.save(p)

    tasks = []
    for item in COMDTS_DATA:
        num = item["art_num"]
        tasks.append(gen_en(num, item["writeup_en"], item["title_en"]))
        tasks.append(gen_hi(num, item["writeup_hi"], item["title_hi"]))
    
    await asyncio.gather(*tasks)
    print("English and Hindi audio synthesized successfully!", flush=True)

    # Punjabi via gTTS
    print("Synthesizing Punjabi audio recitations via gTTS...", flush=True)
    for idx, item in enumerate(COMDTS_DATA, 1):
        num = item["art_num"]
        p = f"assets/audio_pa/audio_{num}.mp3"
        speech_text = f"{item['title_pa']}। {item['writeup_pa']}"
        try:
            tts = gTTS(speech_text, lang='pa')
            tts.save(p)
            print(f"[{idx}/32] Punjabi audio generated for art{num}")
        except Exception as e:
            print(f"Error generating PA art{num}: {e}")

def main():
    print("=== STARTING COMMANDANTS GALLERY OVERHAUL ===", flush=True)
    total = len(COMDTS_DATA)
    for idx, item in enumerate(COMDTS_DATA):
        prev_num = COMDTS_DATA[idx - 1]["art_num"] if idx > 0 else None
        next_num = COMDTS_DATA[idx + 1]["art_num"] if idx < total - 1 else None
        piece_idx = idx + 1

        # Generate English, Hindi, and Punjabi pages
        generate_html_page(item, 'en', prev_num, next_num, total, piece_idx)
        generate_html_page(item, 'hi', prev_num, next_num, total, piece_idx)
        generate_html_page(item, 'pa', prev_num, next_num, total, piece_idx)

    print(f"Generated 96 HTML pages (32 EN, 32 HI, 32 PA) for Commandants' Gallery!", flush=True)

    update_index_dropdowns()

    asyncio.run(synthesize_audio_recitations())

    print("=== COMMANDANTS GALLERY OVERHAUL COMPLETED SUCCESSFULLY! ===", flush=True)

if __name__ == "__main__":
    main()
