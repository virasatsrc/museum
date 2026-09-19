import os
import sys
import re
import json
import asyncio
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import edge_tts
from gtts import gTTS

sys.stdout.reconfigure(encoding='utf-8')

# The 18 battles in gallery order
BATTLES_DATA = [
    {
        "art_num": 401,
        "title_en": "Neuve Chapelle & La Bassee (1914)",
        "title_hi": "न्यूव शापेल और ला बसे (1914)",
        "title_pa": "ਨਿਊਵ ਸ਼ਾਪੇਲ ਅਤੇ ਲਾ ਬਾਸੀ (1914)",
        "year_en": "1914",
        "year_hi": "1914",
        "year_pa": "1914",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈਲਰੀ",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "In October 1914, the Indian Expeditionary Force arrived in France during the desperate opening months of World War I. The Germans launched a fierce breakthrough south of Neuve Chapelle. XLVII Sikhs (47th Sikhs) and Sappers & Miners were thrust into intense trench warfare at Neuve Chapelle and La Bassee. Displaying legendary tenacity and ferocious hand-to-hand fighting, the Sikhs charged German trenches under devastating machine-gun and artillery fire. Though outnumbered and suffering heavy casualties, their valiant counter-attacks halted the German advance, earning immortal renown on the Western Front.",
        "summary_hi": "अक्टूबर 1914 में प्रथम विश्व युद्ध के दौरान भारतीय सेना फ्रांस पहुंची। जर्मन सेना ने न्यूव शापेल के दक्षिण में भीषण आक्रमण किया। 47वीं सिख और सैपर्स एंड माइनर्स को न्यूव शापेल और ला बसे में मोर्चा संभालने का दायित्व मिला। भारी तोपखाने और मशीन गन की गोलीबारी के बीच सिख सैनिकों ने अदम्य साहस दिखाते हुए आमने-सामने की लड़ाई में जर्मन खाइयों पर धावा बोल दिया। अत्यधिक विषम परिस्थितियों और भारी बलिदान के बावजूद उनके जांबाज जवाबी हमले ने जर्मन सेना की बढ़त को रोक दिया और पश्चिमी मोर्चे पर अमर ख्याति प्राप्त की।",
        "summary_pa": "ਅਕਤੂਬਰ 1914 ਵਿੱਚ ਪਹਿਲੇ ਵਿਸ਼ਵ ਯੁੱਧ ਦੌਰਾਨ ਭਾਰਤੀ ਫੌਜ ਫਰਾਂਸ ਪਹੁੰਚੀ। ਜਰਮਨ ਫੌਜ ਨੇ ਨਿਊਵ ਸ਼ਾਪੇਲ ਵਿਖੇ ਭਾਰੀ ਹਮਲਾ ਕੀਤਾ। 47ਵੀਂ ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਅਤੇ ਸੈਪਰਜ਼ ਨੇ ਨਿਊਵ ਸ਼ਾਪੇਲ ਅਤੇ ਲਾ ਬਾਸੀ ਦੇ ਮੋਰਚੇ 'ਤੇ ਜਰਮਨਾਂ ਦਾ ਡਟ ਕੇ ਮੁਕਾਬਲਾ ਕੀਤਾ। ਭਾਰੀ ਗੋਲੀਬਾਰੀ ਦੇ ਬਾਵਜੂਦ ਸਿੱਖ ਸੈਨਿਕਾਂ ਨੇ ਬੇਮਿਸਾਲ ਦਲੇਰੀ ਦਿਖਾਉਂਦਿਆਂ ਜਰਮਨ ਖਾਈਆਂ 'ਤੇ ਹੱਥੋ-ਹੱਥ ਲੜਾਈ ਵਿੱਚ ਹਮਲਾ ਕੀਤਾ। ਬਹੁਤ ਸਾਰੀਆਂ ਸ਼ਹਾਦਤਾਂ ਦੇ ਬਾਵਜੂਦ ਸਿੱਖ ਯੋਧਿਆਂ ਨੇ ਜਰਮਨ ਫੌਜ ਦੇ ਵਾਧੇ ਨੂੰ ਠੱਲ੍ਹ ਪਾਈ ਅਤੇ ਵਿਸ਼ਵ ਭਰ ਵਿੱਚ ਬਹਾਦਰੀ ਦਾ ਨਵਾਂ ਇਤਿਹਾਸ ਰਚਿਆ।"
    },
    {
        "art_num": 421,
        "title_en": "Battle of Ypres (1915)",
        "title_hi": "यिप्रेस की लड़ाई (1915)",
        "title_pa": "ਵਾਈਪ੍ਰੇਸ ਦੀ ਲੜਾਈ (1915)",
        "year_en": "1915",
        "year_hi": "1915",
        "year_pa": "1915",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈਲਰੀ",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "In April and May 1915 during the Second Battle of Ypres in Belgium, 47th Sikhs and 15th Ludhiana Sikhs faced deadly German chlorine gas attacks and overwhelming artillery bombardments. Despite lacking adequate protective gear, the Sikh soldiers held their shattered trenches with unyielding resolve. Launching ferocious bayonet counter-attacks across poison-gas swept battlegrounds, they repelled repeated German onslaughts to protect the strategic Ypres Salient. Their supreme sacrifice, fortitude in the face of chemical warfare, and unbreakable discipline earned the Sikh Regiment prestigious battle honours and worldwide admiration.",
        "summary_hi": "अप्रैल-मई 1915 में बेल्जियम में यिप्रेस के दूसरे युद्ध के दौरान 47वीं सिख और 15वीं लुधियाना सिख ने जर्मन सेना के जहरीले क्लोरीन गैस हमलों और भारी तोपखाने का सामना किया। पर्याप्त सुरक्षा उपकरण न होने के बावजूद सिख योद्धाओं ने अटूट संकल्प के साथ खाइयों की रक्षा की। जहरीली गैस से भरे युद्धक्षेत्र में संगीनों से भीषण जवाबी हमला करते हुए उन्होंने रणनीतिक यिप्रेस क्षेत्र को बचाया। रासायनिक युद्ध के सामने उनकी अद्वितीय वीरता और सर्वोच्च बलिदान ने सिख रेजिमेंट को अमर युद्ध सम्मान दिलाया।",
        "summary_pa": "ਅਪ੍ਰੈਲ-ਮਈ 1915 ਵਿੱਚ ਬੈਲਜੀਅਮ ਵਿਖੇ ਵਾਈਪ੍ਰੇਸ ਦੀ ਦੂਜੀ ਲੜਾਈ ਦੌਰਾਨ 47ਵੀਂ ਸਿੱਖ ਅਤੇ 15ਵੀਂ ਲੁਧਿਆਣਾ ਸਿੱਖ ਨੇ ਜਰਮਨ ਫੌਜ ਦੇ ਜ਼ਹਿਰੀਲੇ ਕਲੋਰੀਨ ਗੈਸ ਹਮਲਿਆਂ ਦਾ ਸਾਹਮਣਾ ਕੀਤਾ। ਸੁਰੱਖਿਆ ਸਾਧਨਾਂ ਦੀ ਘਾਟ ਦੇ ਬਾਵਜੂਦ ਸਿੱਖ ਸੈਨਿਕਾਂ ਨੇ ਦ੍ਰਿੜ ਇਰਾਦੇ ਨਾਲ ਮੋਰਚੇ ਸੰਭਾਲੇ ਰੱਖੇ। ਜ਼ਹਿਰੀਲੀ ਗੈਸ ਦੇ ਦਰਮਿਆਨ ਬੰਦੂਕਾਂ ਦੀਆਂ ਸੰਗੀਨਾਂ ਨਾਲ ਦੁਸ਼ਮਣ 'ਤੇ ਭਾਰੀ ਹਮਲਾ ਬੋਲ ਕੇ ਰਣਨੀਤਕ ਖੇਤਰ ਦੀ ਰੱਖਿਆ ਕੀਤੀ। ਉਨ੍ਹਾਂ ਦੀ ਲਾਮਿਸਾਲ ਕੁਰਬਾਨੀ ਅਤੇ ਬਹਾਦਰੀ ਨੇ ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦਾ ਨਾਂ ਦੁਨੀਆ ਭਰ ਵਿੱਚ ਰੌਸ਼ਨ ਕੀਤਾ।"
    },
    {
        "art_num": 402,
        "title_en": "Battle of Gallipoli (1915)",
        "title_hi": "गैलीपोली का युद्ध (1915)",
        "title_pa": "ਗੈਲੀਪੋਲੀ ਦੀ ਲੜਾਈ (1915)",
        "year_en": "1915",
        "year_hi": "1915",
        "year_pa": "1915",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈਲਰੀ",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "In June 1915 during the Gallipoli Campaign, the 14th Ferozepore Sikhs were tasked with capturing heavily fortified Turkish redoubts and machine-gun nests along Gully Ravine on the Third Battle of Krithia. Charging fearlessly up steep, barbed-wire entrenched slopes under withering crossfire, the Sikhs pressed the assault with unmatched heroism. Out of 514 officers and men who went into battle, 379 laid down their lives or were wounded, fighting to the last bullet. General Sir Ian Hamilton praised their valour, noting that the Sikhs died holding their ground without retreating an inch.",
        "summary_hi": "जून 1915 में गैलीपोली अभियान के दौरान 14वीं फिरोजपुर सिख को क्रिथिया की तीसरी लड़ाई में गली खड्ड के पास मजबूत तुर्की मोर्चों और मशीन गन चौकियों पर कब्जा करने का आदेश मिला। कांटेदार तारों और भयंकर गोलीबारी के बीच सिख सैनिकों ने अदम्य साहस से खड़ी पहाड़ियों पर चढ़ाई की। युद्ध में गए 514 सैनिकों में से 379 वीरगति को प्राप्त हुए या घायल हुए, पर वे अंत तक लड़े। ब्रिटिश कमांडर सर इयान हैमिल्टन ने उनकी वीरता की सराहना करते हुए कहा कि सिख एक इंच भी पीछे हटे बिना अपने मोर्चे पर शहीद हुए।",
        "summary_pa": "ਜੂਨ 1915 ਵਿੱਚ ਗੈਲੀਪੋਲੀ ਮੁਹਿੰਮ ਦੌਰਾਨ 14ਵੀਂ ਫਿਰੋਜ਼ਪੁਰ ਸਿੱਖ ਨੂੰ ਗਲੀ ਰੈਵਿਨ ਵਿਖੇ ਤੁਰਕੀ ਦੇ ਮਜ਼ਬੂਤ ਮੋਰਚਿਆਂ 'ਤੇ ਹਮਲਾ ਕਰਨ ਦਾ ਕੰਮ ਸੌਂਪਿਆ ਗਿਆ। ਕੰਡਿਆਲੀਆਂ ਤਾਰਾਂ ਅਤੇ ਲਗਾਤਾਰ ਗੋਲੀਬਾਰੀ ਦੇ ਬਾਵਜੂਦ ਸਿੱਖਾਂ ਨੇ ਬੇਮਿਸਾਲ ਦਲੇਰੀ ਨਾਲ ਹਮਲਾ ਬੋਲਿਆ। ਮੈਦਾਨ ਵਿੱਚ ਗਏ 514 ਜਵਾਨਾਂ ਵਿੱਚੋਂ 379 ਸ਼ਹੀਦ ਜਾਂ ਜ਼ਖਮੀ ਹੋ ਗਏ ਪਰ ਇੱਕ ਕਦਮ ਵੀ ਪਿੱਛੇ ਨਹੀਂ ਹਟੇ। ਜਨਰਲ ਸਰ ਇਆਨ ਹੈਮਿਲਟਨ ਨੇ ਸ਼ਲਾਘਾ ਕਰਦਿਆਂ ਲਿਖਿਆ ਕਿ ਸਿੱਖਾਂ ਨੇ ਆਪਣੀ ਜਗ੍ਹਾ 'ਤੇ ਡਟੇ ਰਹਿ ਕੇ ਸ਼ਹਾਦਤ ਦਾ ਜਾਮ ਪੀਤਾ।"
    },
    {
        "art_num": 403,
        "title_en": "Battle of Hai (1917)",
        "title_hi": "हाई की लड़ाई (1917)",
        "title_pa": "ਹਾਈ ਦੀ ਲੜਾਈ (1917)",
        "year_en": "1917",
        "year_hi": "1917",
        "year_pa": "1917",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈਲਰੀ",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "On 01 February 1917 in Mesopotamia (modern-day Iraq), 45th Rattray's Sikhs and 36th Sikhs spearheaded a critical offensive across the frozen, muddy Hai River against entrenched Ottoman Turkish positions defending Kut-al-Amara. Under blistering machine-gun and sniper fire across open terrain, the Sikhs breached multiple defensive lines through sheer courage and savage hand-to-hand trench combat. Overcoming immense casualties and severe weather, they captured vital Turkish strongpoints, paving the way for the historic liberation of Baghdad and etching the Battle of Hai into regimental lore.",
        "summary_hi": "1 फरवरी 1917 को मेसोपोटामिया (वर्तमान इराक) में 45वीं रैट्रेज सिख और 36वीं सिख ने कुत-अल-अमारा की रक्षा कर रही तुर्की सेना के खिलाफ हाई नदी के पार एक बड़ा हमला किया। खुले मैदान में भीषण मशीन गन और स्नाइपर गोलीबारी के बीच, सिख सैनिकों ने अदम्य वीरता और खाइयों में आमने-सामने की लड़ाई से दुश्मन की रक्षा पंक्तियों को ध्वस्त कर दिया। भारी नुकसान के बावजूद उन्होंने महत्वपूर्ण ठिकानों पर कब्जा किया, जिससे बगदाद की ऐतिहासिक मुक्ति का मार्ग प्रशस्त हुआ।",
        "summary_pa": "1 ਫਰਵਰੀ 1917 ਨੂੰ ਮੈਸੋਪੋਟੇਮੀਆ (ਮੌਜੂਦਾ ਇਰਾਕ) ਵਿਖੇ 45ਵੀਂ ਰੈਟ੍ਰੇਜ਼ ਸਿੱਖ ਅਤੇ 36ਵੀਂ ਸਿੱਖ ਨੇ ਹਾਈ ਦਰਿਆ ਦੇ ਪਾਰ ਤੁਰਕੀ ਫੌਜ ਦੀਆਂ ਮਜ਼ਬੂਤ ਖਾਈਆਂ 'ਤੇ ਜ਼ਬਰਦਸਤ ਹਮਲਾ ਕੀਤਾ। ਖੁੱਲ੍ਹੇ ਮੈਦਾਨ ਵਿੱਚ ਭਾਰੀ ਗੋਲੀਬਾਰੀ ਦੇ ਬਾਵਜੂਦ ਸਿੱਖਾਂ ਨੇ ਦਲੇਰੀ ਅਤੇ ਆਹਮੋ-ਸਾਹਮਣੇ ਦੀ ਲੜਾਈ ਨਾਲ ਦੁਸ਼ਮਣ ਦੇ ਮੋਰਚੇ ਤੋੜ ਦਿੱਤੇ। ਭਾਰੀ ਕੁਰਬਾਨੀਆਂ ਦੇ ਬਾਵਜੂਦ ਉਨ੍ਹਾਂ ਨੇ ਅਹਿਮ ਚੌਕੀਆਂ 'ਤੇ ਕਬਜ਼ਾ ਕੀਤਾ, ਜਿਸ ਨੇ ਬਗਦਾਦ ਦੀ ਜਿੱਤ ਦਾ ਰਾਹ ਪੱਧਰਾ ਕੀਤਾ।"
    },
    {
        "art_num": 404,
        "title_en": "Battle of Keren (1941)",
        "title_hi": "केरेन की लड़ाई (1941)",
        "title_pa": "ਕੇਰੇਨ ਦੀ ਲੜਾਈ (1941)",
        "year_en": "1941",
        "year_hi": "1941",
        "year_pa": "1941",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈਲਰੀ",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "In February and March 1941 during the East African Campaign of World War II, 4/11 Sikh assaulted the near-impregnable mountain fortress of Keren in Eritrea, fiercely defended by elite Italian troops. Facing sheer cliffs, heavy artillery, and entrenched fortifications, the Sikhs launched audacious assaults against features like Brigade Peak and Cameron Ridge. Through relentless courage, expert mountain warfare, and indomitable spirit, the Sikhs dismantled the Italian bastion. Their decisive victory broke Italian control in East Africa and earned the battalion legendary acclaim.",
        "summary_hi": "फरवरी-मार्च 1941 में द्वितीय विश्व युद्ध के दौरान पूर्वी अफ्रीकी अभियान में 4/11 सिख ने इरिट्रिया में केरेन के अजेय पहाड़ी किले पर हमला किया, जहां इतालवी सेना मजबूत स्थिति में थी। सीधी चट्टानों, भारी तोपखाने और मजबूत मोर्चों का सामना करते हुए सिख सैनिकों ने ब्रिगेड पीक और कैमरून रिज पर साहसिक हमले किए। असाधारण युद्ध कौशल और अदम्य साहस से सिखों ने इतालवी गढ़ को ध्वस्त कर दिया। इस निर्णायक जीत ने पूर्वी अफ्रीका में इतालवी नियंत्रण को समाप्त कर दिया।",
        "summary_pa": "ਫਰਵਰੀ-ਮਾਰਚ 1941 ਵਿੱਚ ਦੂਜੇ ਵਿਸ਼ਵ ਯੁੱਧ ਦੌਰਾਨ ਪੂਰਬੀ ਅਫਰੀਕਾ ਮੁਹਿੰਮ ਵਿੱਚ 4/11 ਸਿੱਖ ਨੇ ਇਰੀਟਰੀਆ ਦੇ ਅਜਿੱਤ ਪਹਾੜੀ ਕਿਲ੍ਹੇ ਕੇਰੇਨ 'ਤੇ ਹਮਲਾ ਬੋਲਿਆ। ਖੜ੍ਹੀਆਂ ਚੱਟਾਨਾਂ ਅਤੇ ਇਤਾਲਵੀ ਫੌਜ ਦੀ ਭਾਰੀ ਗੋਲੀਬਾਰੀ ਦੇ ਬਾਵਜੂਦ ਸਿੱਖਾਂ ਨੇ ਬ੍ਰਿਗੇਡ ਪੀਕ ਅਤੇ ਕੈਮਰੂਨ ਰਿਜ 'ਤੇ ਦਲੇਰਾਨਾ ਹਮਲੇ ਕੀਤੇ। ਆਪਣੇ ਸ਼ਾਨਦਾਰ ਪਹਾੜੀ ਯੁੱਧ ਕੌਸ਼ਲ ਅਤੇ ਬੇਮਿਸਾਲ ਦਲੇਰੀ ਨਾਲ ਸਿੱਖਾਂ ਨੇ ਦੁਸ਼ਮਣ ਦੇ ਪੈਰ ਉਖਾੜ ਦਿੱਤੇ ਅਤੇ ਪੂਰਬੀ ਅਫਰੀਕਾ ਵਿੱਚ ਜਿੱਤ ਦਰਜ ਕੀਤੀ।"
    },
    {
        "art_num": 405,
        "title_en": "Burma Campaign (1941-45)",
        "title_hi": "बर्मा अभियान (1941-45)",
        "title_pa": "ਬਰਮਾ ਮੁਹਿੰਮ (1941-45)",
        "year_en": "1941-45",
        "year_hi": "1941-45",
        "year_pa": "1941-45",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈਲਰੀ",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "From 1942 to 1945, battalions of the Sikh Regiment fought relentlessly across dense jungles and rugged hills during the Burma Campaign against Imperial Japanese forces. Battles across Sittang Bridge, Arakan, Imphal, Kohima, and the Irrawaddy River tested the limits of endurance. The Sikhs demonstrated supreme combat skills in close-quarter jungle fighting, earning two Victoria Crosses and numerous decorations. Their resilience, courage, and relentless counter-offensives played a pivotal role in shattering Japanese forces and liberating Burma.",
        "summary_hi": "1942 से 1945 तक द्वितीय विश्व युद्ध के बर्मा अभियान में सिख रेजिमेंट की बटालियनों ने जापानी सेना के खिलाफ घने जंगलों और दुर्गम पहाड़ियों में लगातार युद्ध लड़ा। सितांग ब्रिज, अराकान, इंफाल, कोहिमा और इरावदी नदी की लड़ाइयों में सिखों ने अद्वितीय सहनशक्ति और जंगल युद्ध कला का प्रदर्शन किया। रेजिमेंट के जांबाजों ने दो विक्टोरिया क्रॉस सहित कई वीरता पुरस्कार जीते। उनके अदम्य साहस और दृढ़ संकल्प ने जापानी सेना को परास्त कर बर्मा की मुक्ति में निर्णायक भूमिका निभाई।",
        "summary_pa": "1942 ਤੋਂ 1945 ਤੱਕ ਬਰਮਾ ਮੁਹਿੰਮ ਦੌਰਾਨ ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦੀਆਂ ਬਟਾਲੀਅਨਾਂ ਨੇ ਜਾਪਾਨੀ ਫੌਜਾਂ ਵਿਰੁੱਧ ਸੰਘਣੇ ਜੰਗਲਾਂ ਅਤੇ ਪਹਾੜਾਂ ਵਿੱਚ ਲਗਾਤਾਰ ਲੜਾਈਆਂ ਲੜੀਆਂ। ਸਿਤਾਂਗ ਬ੍ਰਿਜ, ਅਰਾਕਾਨ, ਇੰਫਾਲ, ਕੋਹੀਮਾ ਅਤੇ ਇਰਾਵਦੀ ਦਰਿਆ ਦੇ ਮੋਰਚਿਆਂ 'ਤੇ ਸਿੱਖਾਂ ਨੇ ਬੇਮਿਸਾਲ ਜੰਗਲ ਯੁੱਧ ਕਲਾ ਦਿਖਾਈ। ਇਸ ਮੁਹਿੰਮ ਵਿੱਚ ਦੋ ਵਿਕਟੋਰੀਆ ਕਰਾਸ ਅਤੇ ਅਣਗਿਣਤ ਬਹਾਦਰੀ ਪੁਰਸਕਾਰ ਪ੍ਰਾਪਤ ਕਰਕੇ ਸਿੱਖ ਯੋਧਿਆਂ ਨੇ ਜਾਪਾਨੀ ਫੌਜ ਨੂੰ ਹਰਾਉਣ ਵਿੱਚ ਇਤਿਹਾਸਕ ਯੋਗਦਾਨ ਪਾਇਆ।"
    },
    {
        "art_num": 406,
        "title_en": "Battle of Shalateng (1947)",
        "title_hi": "शालतेंग का युद्ध (1947)",
        "title_pa": "ਸ਼ਾਲਤੈਂਗ ਦੀ ਲੜਾਈ (1947)",
        "year_en": "1947",
        "year_hi": "1947",
        "year_pa": "1947",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈਲਰੀ",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "On 07 November 1947, 1 SIKH, alongside 1 Kumaon and armored cars of 7 Cavalry, executed a masterclass in tactical warfare at Shalateng, just outside Srinagar. Facing over 2,000 heavily armed tribal raiders advancing on Srinagar, Indian troops launched a coordinated three-pronged encirclement attack supported by air strikes. The Sikhs' decisive frontal assault shattered the raiders, inflicting over 300 enemy casualties and capturing massive stockpiles of weapons. This landmark victory permanently saved Srinagar and the Kashmir Valley.",
        "summary_hi": "7 नवंबर 1947 को 1 सिख ने 1 कुमाऊं और 7 कैवेलरी के साथ मिलकर श्रीनगर के निकट शालतेंग में ऐतिहासिक युद्ध लड़ा। श्रीनगर की ओर बढ़ रहे 2,000 से अधिक हथियारों से लैस कबाइलियों के सामने भारतीय सेना ने तीनों दिशाओं से घेरकर हवाई हमलों के साथ भीषण आक्रमण किया। सिखों के सटीक और शक्तिशाली हमले ने हमलावरों को तितर-बितर कर दिया, 300 से अधिक दुश्मन मारे गए और भारी मात्रा में हथियार बरामद हुए। इस जीत ने श्रीनगर और कश्मीर घाटी को हमेशा के लिए बचा लिया।",
        "summary_pa": "7 ਨਵੰਬਰ 1947 ਨੂੰ 1 ਸਿੱਖ ਨੇ 1 ਕੁਮਾਉਂ ਅਤੇ 7 ਕੈਵਲਰੀ ਨਾਲ ਮਿਲ ਕੇ ਸ਼੍ਰੀਨਗਰ ਨੇੜੇ ਸ਼ਾਲਤੈਂਗ ਵਿਖੇ ਇਤਿਹਾਸਕ ਲੜਾਈ ਲੜੀ। ਸ਼੍ਰੀਨਗਰ ਵੱਲ ਵਧ ਰਹੇ 2,000 ਤੋਂ ਵੱਧ ਹਥਿਆਰਬੰਦ ਕਬਾਇਲੀਆਂ 'ਤੇ ਤਿੰਨਾਂ ਪਾਸਿਆਂ ਤੋਂ ਘੇਰਾ ਪਾ ਕੇ ਹਵਾਈ ਸਹਾਇਤਾ ਨਾਲ ਜ਼ਬਰਦਸਤ ਹਮਲਾ ਕੀਤਾ ਗਿਆ। ਸਿੱਖਾਂ ਦੇ ਤੇਜ਼ ਅਤੇ ਸ਼ਕਤੀਸ਼ਾਲੀ ਹਮਲੇ ਨੇ ਦੁਸ਼ਮਣ ਦਾ ਲੱਕ ਤੋੜ ਦਿੱਤਾ, ਜਿਸ ਨਾਲ 300 ਤੋਂ ਵੱਧ ਹਮਲਾਵਰ ਮਾਰੇ ਗਏ ਅਤੇ ਸ਼੍ਰੀਨਗਰ ਤੇ ਕਸ਼ਮੀਰ ਵਾਦੀ ਪੂਰੀ ਤਰ੍ਹਾਂ ਸੁਰੱਖਿਅਤ ਹੋ ਗਈ।"
    },
    {
        "art_num": 407,
        "title_en": "Capture of Richhmar Gali (1948)",
        "title_hi": "रीछमार गली पर विजय (1948)",
        "title_pa": "ਰਿਛਮਾਰ ਗਲੀ 'ਤੇ ਕਬਜ਼ਾ (1948)",
        "year_en": "1948",
        "year_hi": "1948",
        "year_pa": "1948",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈਲਰੀ",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "In May 1948 during operations in the Tithwal Sector of Jammu and Kashmir, 1 SIKH under Lieutenant Colonel Kehar Singh was tasked with capturing the rugged, heavily fortified high-altitude feature of Richhmar Gali. In freezing temperatures and under intense enemy mortar and automatic fire, the Sikhs scaled precipitous mountain heights and launched a fierce bayonet assault. Overwhelming enemy resistance, they secured Richhmar Gali, denying Pakistan a strategic infiltration route into the Kashmir Valley.",
        "summary_hi": "मई 1948 में जम्मू-कश्मीर के तंगधार-टिथवाल सेक्टर में 1 सिख ने लेफ्टिनेंट कर्नल केहर सिंह के नेतृत्व में दुर्गम और भारी किलेबंद रीछमार गली पर कब्जा करने का अभियान चलाया। शून्य से नीचे तापमान और भारी मोर्टार व स्वचालित हथियारों की गोलीबारी के बीच, सिख सैनिकों ने खड़ी पहाड़ियों पर चढ़कर संगीनों से भीषण हमला किया। दुश्मन के कड़े प्रतिरोध को ध्वस्त करते हुए रीछमार गली पर तिरंगा फहराया और कश्मीर में घुसपैठ के रास्ते बंद कर दिए।",
        "summary_pa": "ਮਈ 1948 ਵਿੱਚ ਜੰਮੂ ਅਤੇ ਕਸ਼ਮੀਰ ਦੇ ਟਿੱਥਵਾਲ ਸੈਕਟਰ ਵਿੱਚ 1 ਸਿੱਖ ਨੇ ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਕੇਹਰ ਸਿੰਘ ਦੀ ਅਗਵਾਈ ਹੇਠ ਉੱਚੀ ਅਤੇ ਦੁਰਗਮ ਰਿਛਮਾਰ ਗਲੀ 'ਤੇ ਕਬਜ਼ਾ ਕਰਨ ਦਾ ਅਭਿਆਨ ਚਲਾਇਆ। ਕੜਾਕੇ ਦੀ ਠੰਢ ਅਤੇ ਦੁਸ਼ਮਣ ਦੀ ਭਾਰੀ ਗੋਲੀਬਾਰੀ ਦੇ ਬਾਵਜੂਦ ਸਿੱਖ ਯੋਧਿਆਂ ਨੇ ਪਹਾੜੀਆਂ ਚੜ੍ਹ ਕੇ ਸੰਗੀਨਾਂ ਨਾਲ ਹਮਲਾ ਕੀਤਾ। ਦੁਸ਼ਮਣ ਨੂੰ ਭਾਰੀ ਨੁਕਸਾਨ ਪਹੁੰਚਾ ਕੇ ਰਿਛਮਾਰ ਗਲੀ 'ਤੇ ਕਬਜ਼ਾ ਕੀਤਾ ਅਤੇ ਕਸ਼ਮੀਰ ਵਾਦੀ ਦੀ ਸੁਰੱਖਿਆ ਮਜ਼ਬੂਤ ਕੀਤੀ।"
    },
    {
        "art_num": 408,
        "title_en": "Defence of Tawang (1962)",
        "title_hi": "तवांग का बचाव (1962)",
        "title_pa": "ਤਵਾਂਗ ਦੀ ਰੱਖਿਆ (1962)",
        "year_en": "1962",
        "year_hi": "1962",
        "year_pa": "1962",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈਲਰੀ",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "In October 1962 during the Sino-Indian War, 1 SIKH was deployed along the Namka Chu river and the high-altitude ridges of Tawang in NEFA (Arunachal Pradesh). Facing massive human-wave assaults and heavy artillery from the Chinese People's Liberation Army, Sikh soldiers fought with legendary courage. Isolated and vastly outnumbered, posts held by the Sikhs resisted tenaciously to the last man and bullet, exacting heavy tolls on the advancing Chinese troops and upholding the highest traditions of Indian military gallantry.",
        "summary_hi": "अक्टूबर 1962 में भारत-चीन युद्ध के दौरान 1 सिख ने नेफा (अरुणाचल प्रदेश) में नामका चू नदी और तवांग की बर्फीली चोटियों पर मोर्चा संभाला। भारी संख्या में चीनी सेना के हमलों और तोपखाने की बमबारी का सामना करते हुए सिख सैनिकों ने अद्भुत वीरता का परिचय दिया। अलग-थलग और संख्या में बहुत कम होने के बावजूद सिख चौकियों ने अंतिम सांस और अंतिम गोली तक संघर्ष किया तथा दुश्मन को भारी क्षति पहुंचाई।",
        "summary_pa": "ਅਕਤੂਬਰ 1962 ਵਿੱਚ ਭਾਰਤ-ਚੀਨ ਜੰਗ ਦੌਰਾਨ 1 ਸਿੱਖ ਨੇ ਅਰੁਣਾਚਲ ਪ੍ਰਦੇਸ਼ ਵਿੱਚ ਨਾਮਕਾ ਚੂ ਦਰਿਆ ਅਤੇ ਤਵਾਂਗ ਦੀਆਂ ਬਰਫੀਲੀਆਂ ਪਹਾੜੀਆਂ 'ਤੇ ਮੋਰਚਾ ਸੰਭਾਲਿਆ। ਚੀਨੀ ਫੌਜ ਦੇ ਭਾਰੀ ਹਮਲਿਆਂ ਅਤੇ ਤੋਪਖਾਨੇ ਦੇ ਬਾਵਜੂਦ ਸਿੱਖ ਸੈਨਿਕਾਂ ਨੇ ਲਾਮਿਸਾਲ ਬਹਾਦਰੀ ਦਿਖਾਈ। ਘੱਟ ਗਿਣਤੀ ਵਿੱਚ ਹੋਣ ਦੇ ਬਾਵਜੂਦ ਸਿੱਖ ਜਵਾਨਾਂ ਨੇ ਆਖਰੀ ਗੋਲੀ ਅਤੇ ਆਖਰੀ ਦਮ ਤੱਕ ਲੜਦਿਆਂ ਦੁਸ਼ਮਣ ਦਾ ਡਟ ਕੇ ਮੁਕਾਬਲਾ ਕੀਤਾ।"
    },
    {
        "art_num": 409,
        "title_en": "Battle of Walong (1962)",
        "title_hi": "वालोंग की लड़ाई (1962)",
        "title_pa": "ਵਾਲੋਂਗ ਦੀ ਲੜਾਈ (1962)",
        "year_en": "1962",
        "year_hi": "1962",
        "year_pa": "1962",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈਲਰੀ",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "In October and November 1962 in the easternmost sector of NEFA, 4 SIKH fought heroically at the Battle of Walong. Outnumbered by waves of Chinese forces, 4 SIKH launched daring counter-attacks on features like Yellow Pimple and Tri-Junction. Fighting without adequate supplies and in rugged mountain terrain, the Sikhs held their positions with stubborn tenacity for three weeks, inflicting devastating casualties on the enemy in one of the most fiercely contested battles of the 1962 War.",
        "summary_hi": "अक्टूबर-नवंबर 1962 में नेफा के पूर्वी छोर पर 4 सिख ने वालोंग की ऐतिहासिक लड़ाई में अदम्य पराक्रम दिखाया। भारी संख्या में चीनी सैनिकों के हमलों के बावजूद 4 सिख ने येलो पिंपल और ट्राई-जंक्शन पर साहसिक जवाबी हमले किए। दुर्गम पहाड़ी क्षेत्र और सीमित संसाधनों के बावजूद सिख सैनिकों ने तीन हफ्तों तक चीनी सेना को रोके रखा और दुश्मन को भारी नुकसान पहुंचाया, जो 1962 के युद्ध का सबसे साहसिक प्रतिरोध माना जाता है।",
        "summary_pa": "ਅਕਤੂਬਰ-ਨਵੰਬਰ 1962 ਵਿੱਚ 4 ਸਿੱਖ ਨੇ ਵਾਲੋਂਗ ਦੀ ਇਤਿਹਾਸਕ ਲੜਾਈ ਵਿੱਚ ਸ਼ਾਨਦਾਰ ਬਹਾਦਰੀ ਦਾ ਪ੍ਰਦਰਸ਼ਨ ਕੀਤਾ। ਚੀਨੀ ਫੌਜ ਦੇ ਵੱਡੇ ਹਮਲਿਆਂ ਦੇ ਬਾਵਜੂਦ 4 ਸਿੱਖ ਨੇ ਯੈਲੋ ਪਿੰਪਲ ਅਤੇ ਟ੍ਰਾਈ-ਜੰਕਸ਼ਨ 'ਤੇ ਜ਼ਬਰਦਸਤ ਜਵਾਬੀ ਹਮਲੇ ਕੀਤੇ। ਸੀਮਤ ਸਾਧਨਾਂ ਦੇ ਬਾਵਜੂਦ ਸਿੱਖਾਂ ਨੇ ਤਿੰਨ ਹਫ਼ਤਿਆਂ ਤੱਕ ਦੁਸ਼ਮਣ ਨੂੰ ਅੱਗੇ ਵਧਣ ਤੋਂ ਰੋਕੀ ਰੱਖਿਆ ਅਤੇ ਭਾਰੀ ਨੁਕਸਾਨ ਪਹੁੰਚਾਇਆ।"
    },
    {
        "art_num": 410,
        "title_en": "Battle of Barki (1965)",
        "title_hi": "बरकी की लड़ाई (1965)",
        "title_pa": "ਬਾਰਕੀ ਦੀ ਲੜਾਈ (1965)",
        "year_en": "1965",
        "year_hi": "1965",
        "year_pa": "1965",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈਲਰੀ",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "On 10 September 1965 during the Indo-Pak War, 4 SIKH led a daring night assault to capture the heavily fortified town of Barki along the strategic Ichhogil Canal near Lahore. Facing intense fire from concrete pillboxes, anti-tank guns, and tanks, the Sikhs charged with cold steel and ferocity. Spearheaded by company commanders and soldiers who crawled through mud to eliminate enemy bunkers with grenades, 4 SIKH captured Barki, securing a major victory on the Western Front.",
        "summary_hi": "10 सितंबर 1965 को भारत-पाक युद्ध के दौरान 4 सिख ने लाहौर के निकट रणनीतिक इच्छोगिल नहर पर स्थित बरकी नगर पर कब्जा करने के लिए रात में साहसिक हमला किया। कंक्रीट के बंकरों, टैंकों और तोपों की भीषण गोलीबारी के सामने सिख सैनिकों ने संगीनों और हथगोलों से दुश्मन के बंकरों को नेस्तनाबूद कर दिया। अदम्य वीरता का प्रदर्शन करते हुए 4 सिख ने बरकी पर विजय प्राप्त की, जो 1965 के युद्ध की ऐतिहासिक जीत बनी।",
        "summary_pa": "10 ਸਤੰਬਰ 1965 ਨੂੰ ਭਾਰਤ-ਪਾਕਿ ਜੰਗ ਦੌਰਾਨ 4 ਸਿੱਖ ਨੇ ਲਾਹੌਰ ਨੇੜੇ ਇੱਛੋਗਿਲ ਨਹਿਰ 'ਤੇ ਸਥਿਤ ਬਾਰਕੀ ਕਸਬੇ 'ਤੇ ਰਾਤ ਵੇਲੇ ਦਲੇਰਾਨਾ ਹਮਲਾ ਕੀਤਾ। ਕੰਕਰੀਟ ਦੇ ਬੰਕਰਾਂ ਅਤੇ ਟੈਂਕਾਂ ਦੀ ਭਾਰੀ ਗੋਲੀਬਾਰੀ ਦੇ ਬਾਵਜੂਦ ਸਿੱਖਾਂ ਨੇ ਸੰਗੀਨਾਂ ਅਤੇ ਗ੍ਰਨੇਡਾਂ ਨਾਲ ਦੁਸ਼ਮਣ ਦੇ ਮੋਰਚੇ ਤਬਾਹ ਕਰ ਦਿੱਤੇ। ਬੇਮਿਸਾਲ ਦਲੇਰੀ ਨਾਲ 4 ਸਿੱਖ ਨੇ ਬਾਰਕੀ 'ਤੇ ਕਬਜ਼ਾ ਕਰਕੇ ਸ਼ਾਨਦਾਰ ਜਿੱਤ ਪ੍ਰਾਪਤ ਕੀਤੀ।"
    },
    {
        "art_num": 411,
        "title_en": "Battle of Raja Picquet (1965)",
        "title_hi": "राजा पिक्वेट का युद्ध (1965)",
        "title_pa": "ਰਾਜਾ ਪਿਕੇਟ ਦੀ ਲੜਾਈ (1965)",
        "year_en": "1965",
        "year_hi": "1965",
        "year_pa": "1965",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈਲਰੀ",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "In September 1965 in the Poonch Sector, 2 SIKH under Lieutenant Colonel NN Khanna was tasked with capturing Raja Picquet, a formidable 7,000-foot enemy stronghold dominating the Poonch-Hajipir link. On the night of 02 October, the Sikhs scaled sheer razor-sharp cliffs in total darkness under blistering artillery and machine-gun fire. Displaying supreme bravery, Lieutenant Colonel Khanna was fatally wounded leading from the front. The Sikhs stormed and captured the fortress, immortalizing the battle in regimental history.",
        "summary_hi": "सितंबर 1965 में पुंछ सेक्टर में 2 सिख को 7,000 फीट ऊंची दुर्गम पहाड़ी पर स्थित पाकिस्तानी गढ़ राजा पिक्वेट पर कब्जा करने का कार्य सौंपा गया। 2 अक्टूबर की रात को लेफ्टिनेंट कर्नल एनएन खन्ना के नेतृत्व में सिख सैनिकों ने घने अंधेरे और भीषण तोपखाने की आग के बीच खड़ी चट्टानों पर चढ़ाई की। आगे बढ़कर नेतृत्व करते हुए कर्नल खन्ना वीरगति को प्राप्त हुए, परंतु सिख जवानों ने किले पर विजय प्राप्त कर इतिहास रच दिया।",
        "summary_pa": "ਸਤੰਬਰ 1965 ਵਿੱਚ ਪੂੰਛ ਸੈਕਟਰ ਵਿੱਚ 2 ਸਿੱਖ ਨੂੰ 7,000 ਫੁੱਟ ਉੱਚੀ ਪਹਾੜੀ 'ਤੇ ਸਥਿਤ ਰਾਜਾ ਪਿਕੇਟ 'ਤੇ ਕਬਜ਼ਾ ਕਰਨ ਦਾ ਟੀਚਾ ਦਿੱਤਾ ਗਿਆ। 2 ਅਕਤੂਬਰ ਦੀ ਰਾਤ ਨੂੰ ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਐਨ.ਐਨ. ਖੰਨਾ ਦੀ ਅਗਵਾਈ ਵਿੱਚ ਸਿੱਖਾਂ ਨੇ ਭਾਰੀ ਗੋਲੀਬਾਰੀ ਦਰਮਿਆਨ ਚੱਟਾਨਾਂ ਚੜ੍ਹ ਕੇ ਹਮਲਾ ਕੀਤਾ। ਕਰਨਲ ਖੰਨਾ ਸ਼ਹੀਦ ਹੋ ਗਏ ਪਰ ਸਿੱਖ ਯੋਧਿਆਂ ਨੇ ਦੁਸ਼ਮਣ ਦੇ ਪੈਰ ਉਖਾੜ ਕੇ ਰਾਜਾ ਪਿਕੇਟ 'ਤੇ ਤਿਰੰਗਾ ਲਹਿਰਾਇਆ।"
    },
    {
        "art_num": 412,
        "title_en": "Battle of OP Hill (1965)",
        "title_hi": "ओपी हिल की लड़ाई (1965)",
        "title_pa": "ਓਪੀ ਹਿੱਲ ਦੀ ਲੜਾਈ (1965)",
        "year_en": "1965",
        "year_hi": "1965",
        "year_pa": "1965",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈलरी",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "In November 1965, post-ceasefire in the Mendhar Sector of Jammu and Kashmir, Pakistani troops intruded and heavily fortified OP Hill (Chuh-i-Nar). 2 SIKH and 7 SIKH participated in a multi-battalion assault to clear this critical dominating feature. Charging through minefields and under intense crossfire, Sikh soldiers displayed exemplary grit and valour in brutal close-quarter combat. The Sikhs cleared the Pakistani intrusion, reclaiming OP Hill and restoring full territorial control.",
        "summary_hi": "नवंबर 1965 में युद्धविराम के बाद जम्मू-कश्मीर के मेंढर सेक्टर में पाकिस्तानी सेना ने ओपी हिल (चुह-ए-नार) पर अवैध कब्जा कर किलेबंदी कर ली थी। 2 सिख और 7 सिख ने इस रणनीतिक चोटी को मुक्त कराने के लिए संयुक्त अभियान चलाया। बारूदी सुरंगों और भारी गोलीबारी के बीच सिख सैनिकों ने अदम्य साहस और आमने-सामने की लड़ाई में पाकिस्तानी बंकरों को ध्वस्त कर दिया। सिखों ने ओपी हिल को पूरी तरह मुक्त कराकर तिरंगा फहराया।",
        "summary_pa": "ਨਵੰਬਰ 1965 ਵਿੱਚ ਜੰਗਬੰਦੀ ਤੋਂ ਬਾਅਦ ਮੇਂਧਰ ਸੈਕਟਰ ਵਿੱਚ ਪਾਕਿਸਤਾਨੀ ਫੌਜ ਨੇ ਓਪੀ ਹਿੱਲ 'ਤੇ ਕਬਜ਼ਾ ਕਰ ਲਿਆ ਸੀ। 2 ਸਿੱਖ ਅਤੇ 7 ਸਿੱਖ ਨੇ ਇਸ ਰਣਨੀਤਕ ਚੋਟੀ ਨੂੰ ਆਜ਼ਾਦ ਕਰਵਾਉਣ ਲਈ ਸਾਂਝਾ ਹਮਲਾ ਕੀਤਾ। ਬਾਰੂਦੀ ਸੁਰੰਗਾਂ ਅਤੇ ਭਾਰੀ ਗੋਲੀਬਾਰੀ ਦੇ ਬਾਵਜੂਦ ਸਿੱਖਾਂ ਨੇ ਆਹਮੋ-ਸਾਹਮਣੇ ਦੀ ਲੜਾਈ ਵਿੱਚ ਦੁਸ਼ਮਣ ਨੂੰ ਹਰਾ ਕੇ ਓਪੀ ਹਿੱਲ 'ਤੇ ਦੁਬਾਰਾ ਕਬਜ਼ਾ ਕੀਤਾ।"
    },
    {
        "art_num": 413,
        "title_en": "Defence of Chhamb (1971)",
        "title_hi": "छम्ब का बचाव (1971)",
        "title_pa": "ਛੰਬ ਦੀ ਰੱਖਿਆ (1971)",
        "year_en": "1971",
        "year_hi": "1971",
        "year_pa": "1971",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈਲਰੀ",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "In December 1971 during the Indo-Pak War, 5 SIKH under Lieutenant Colonel Prem Khanna held the critical Chhamb Sector along the Munawar Tawi river. Pakistan launched massive armored and infantry assaults supported by overwhelming artillery. For days, 5 SIKH held fortified positions at Point 303, Phagla, and Mandiala, destroying dozens of enemy tanks and repulsing repeated battalion-strength attacks. Their heroic stand broke the back of the Pakistani offensive, preventing a breakthrough towards Akhnoor.",
        "summary_hi": "दिसंबर 1971 के भारत-पाक युद्ध में 5 सिख ने लेफ्टिनेंट कर्नल प्रेम खन्ना के नेतृत्व में मुनाव्वर तवी नदी के किनारे छम्ब सेक्टर में मोर्चा संभाला। पाकिस्तानी सेना ने भारी तोपखाने, टैंकों और पैदल सेना के साथ भीषण हमला किया। 5 सिख ने प्वाइंट 303, फागला और मंडियाला में डटकर मुकाबला करते हुए दुश्मन के दर्जनों टैंक नष्ट किए और कई हमलों को विफल किया। इस वीरतापूर्ण रक्षा ने अखनूर की ओर पाकिस्तानी बढ़त को पूरी तरह रोक दिया।",
        "summary_pa": "ਦਸੰਬਰ 1971 ਦੀ ਜੰਗ ਵਿੱਚ 5 ਸਿੱਖ ਨੇ ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਪ੍ਰੇਮ ਖੰਨਾ ਦੀ ਅਗਵਾਈ ਹੇਠ ਛੰਬ ਸੈਕਟਰ ਵਿੱਚ ਮੋਰਚਾ ਸੰਭਾਲਿਆ। ਪਾਕਿਸਤਾਨੀ ਫੌਜ ਨੇ ਭਾਰੀ ਟੈਂਕਾਂ ਅਤੇ ਤੋਪਖਾਨੇ ਨਾਲ ਵੱਡਾ ਹਮਲਾ ਕੀਤਾ। 5 ਸਿੱਖ ਨੇ ਪੁਆਇੰਟ 303 ਅਤੇ ਮੰਡਿਆਲਾ ਵਿਖੇ ਡਟ ਕੇ ਮੁਕਾਬਲਾ ਕਰਦਿਆਂ ਦੁਸ਼ਮਣ ਦੇ ਦਰਜਨਾਂ ਟੈਂਕ ਤਬਾਹ ਕੀਤੇ ਅਤੇ ਪਾਕਿਸਤਾਨੀ ਹਮਲੇ ਨੂੰ ਨਾਕਾਮ ਕਰ ਦਿੱਤਾ।"
    },
    {
        "art_num": 414,
        "title_en": "Defence of Poonch (1971)",
        "title_hi": "पुंछ का बचाव (1971)",
        "title_pa": "ਪੂੰਛ ਦੀ ਰੱਖਿਆ (1971)",
        "year_en": "1971",
        "year_hi": "1971",
        "year_pa": "1971",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈਲਰੀ",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "In December 1971, Pakistan launched Operation Grand Slam II employing an entire infantry division to capture Poonch. 6 SIKH was entrusted with defending critical fortified complexes including Helipad Hill and Thanpir. Outnumbered five to one and enduring non-stop artillery barrages, the Sikhs held their ground with ferocious tenacity. Launching spirited counter-attacks and eliminating infiltrating columns in close combat, 6 SIKH decisively defeated the Pakistani assault and protected Poonch from capture.",
        "summary_hi": "दिसंबर 1971 में पाकिस्तानी सेना ने पुंछ पर कब्जा करने के लिए एक पूरा इन्फैंट्री डिवीजन झोंक दिया। 6 सिख को हेलीपैड हिल और थानपीर सहित प्रमुख रक्षा चौकियों की जिम्मेदारी दी गई थी। पांच गुना बड़ी दुश्मन सेना और भारी गोलाबारी के सामने सिख सैनिकों ने चट्टान की तरह डटकर मुकाबला किया। साहसिक जवाबी हमलों में दुश्मन की टुकड़ियों को नष्ट करते हुए 6 सिख ने पाकिस्तानी आक्रमण को पूरी तरह विफल किया और पुंछ की रक्षा की।",
        "summary_pa": "ਦਸੰਬਰ 1971 ਵਿੱਚ ਪਾਕਿਸਤਾਨ ਨੇ ਪੂੰਛ 'ਤੇ ਕਬਜ਼ਾ ਕਰਨ ਲਈ ਆਪਣੀ ਪੂਰੀ ਇਨਫੈਂਟਰੀ ਡਿਵੀਜ਼ਨ ਨਾਲ ਹਮਲਾ ਕੀਤਾ। 6 ਸਿੱਖ ਨੂੰ ਹੈਲੀਪੈਡ ਹਿੱਲ ਅਤੇ ਥਾਨਪੀਰ ਦੀ ਰੱਖਿਆ ਦਾ ਜ਼ਿੰਮਾ ਸੌਂਪਿਆ ਗਿਆ। ਦੁਸ਼ਮਣ ਦੀ ਭਾਰੀ ਗਿਣਤੀ ਅਤੇ ਗੋਲੀਬਾਰੀ ਦੇ ਬਾਵਜੂਦ ਸਿੱਖਾਂ ਨੇ ਅਦੁੱਤੀ ਦਲੇਰੀ ਨਾਲ ਮੁਕਾਬਲਾ ਕੀਤਾ ਅਤੇ ਜਵਾਬੀ ਹਮਲੇ ਕਰਕੇ ਪਾਕਿਸਤਾਨੀ ਹਮਲੇ ਨੂੰ ਨਾਕਾਮ ਕਰਦਿਆਂ ਪੂੰਛ ਨੂੰ ਸੁਰੱਖਿਅਤ ਰੱਖਿਆ।"
    },
    {
        "art_num": 415,
        "title_en": "Battle of Purbut Ali (1971)",
        "title_hi": "पुरबुत अली की लड़ाई (1971)",
        "title_pa": "ਪੁਰਬਤ ਅਲੀ ਦੀ ਲੜਾਈ (1971)",
        "year_en": "1971",
        "year_hi": "1971",
        "year_pa": "1971",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈਲਰੀ",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "In December 1971 on the Western Front in the Sindh desert, 10 SIKH was tasked with capturing Purbut Ali, a heavily fortified 200-foot sand dune ridge dominating the route to Naya Chor. Under relentless machine-gun, artillery, and mortar fire across open sand dunes, the Sikhs launched a daring night assault. Breaching minefields and clearing enemy trenches in ferocious hand-to-hand fighting, 10 SIKH captured Purbut Ali, securing a decisive breakthrough in the desert sector.",
        "summary_hi": "दिसंबर 1971 में सिंध के रेगिस्तान में 10 सिख को पुरबुत अली नामक 200 फीट ऊंचे मजबूत रेत के टीले पर कब्जा करने का दायित्व मिला, जो नया छोर के रास्ते पर स्थित था। खुले रेगिस्तान में भारी मशीन गन और तोपखाने की आग के बीच, सिखों ने रात में साहसिक हमला किया। बारूदी सुरंगों को पार करते हुए आमने-सामने की लड़ाई में खाइयों को साफ किया और पुरबुत अली पर विजय प्राप्त कर रेगिस्तानी मोर्चे पर निर्णायक बढ़त बनाई।",
        "summary_pa": "ਦਸੰਬਰ 1971 ਵਿੱਚ ਸਿੰਧ ਦੇ ਰੇਗਿਸਤਾਨ ਵਿੱਚ 10 ਸਿੱਖ ਨੂੰ ਪੁਰਬਤ ਅਲੀ ਦੀ 200 ਫੁੱਟ ਉੱਚੀ ਮਜ਼ਬੂਤ ਰੇਤਲੀ ਚੋਟੀ 'ਤੇ ਕਬਜ਼ਾ ਕਰਨ ਦਾ ਕੰਮ ਮਿਲਿਆ। ਭਾਰੀ ਗੋਲੀਬਾਰੀ ਦਰਮਿਆਨ ਸਿੱਖਾਂ ਨੇ ਰਾਤ ਵੇਲੇ ਦਲੇਰਾਨਾ ਹਮਲਾ ਕੀਤਾ। ਬਾਰੂਦੀ ਸੁਰੰਗਾਂ ਪਾਰ ਕਰਕੇ ਆਹਮੋ-ਸਾਹਮਣੇ ਦੀ ਲੜਾਈ ਵਿੱਚ ਦੁਸ਼ਮਣ ਨੂੰ ਹਰਾ ਕੇ ਪੁਰਬਤ ਅਲੀ 'ਤੇ ਕਬਜ਼ਾ ਕੀਤਾ ਅਤੇ ਰੇਗਿਸਤਾਨੀ ਮੋਰਚੇ 'ਤੇ ਜਿੱਤ ਹਾਸਲ ਕੀਤੀ।"
    },
    {
        "art_num": 416,
        "title_en": "Battle of Siramani (1971)",
        "title_hi": "सिरमानी की लड़ाई (1971)",
        "title_pa": "ਸਿਰਮਾਨੀ ਦੀ ਲੜਾਈ (1971)",
        "year_en": "1971",
        "year_hi": "1971",
        "year_pa": "1971",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈਲਰੀ",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "In November and December 1971 on the Eastern Front (Bangladesh), 4 SIKH under Lieutenant Colonel DS Sidhu spearheaded the offensive against the heavily fortified fortress of Siramani near Khulna. Pakistani forces were entrenched in concrete bunkers supported by tanks and heavy artillery. In one of the most intense battles of the war, the Sikhs launched repeated assaults through waterlogged marshlands, eliminating pillboxes in fierce bayonet combat and forcing the surrender of the entire Pakistani garrison.",
        "summary_hi": "नवंबर-दिसंबर 1971 में पूर्वी मोर्चे (बांग्लादेश) पर 4 सिख ने लेफ्टिनेंट कर्नल डीएस सिद्धू के नेतृत्व में खुलना के निकट सिरमानी के किलेबंद गढ़ पर भीषण आक्रमण किया। पाकिस्तानी सेना कंक्रीट के बंकरों, टैंकों और तोपों से लैस थी। युद्ध की सबसे भीषण लड़ाइयों में से एक में सिख सैनिकों ने दलदली भूमि के बीच संगीनों से हमला कर बंकरों को ध्वस्त किया और पूरी पाकिस्तानी छावनी को आत्मसमर्पण करने पर मजबूर कर दिया।",
        "summary_pa": "ਨਵੰਬਰ-ਦਸੰਬਰ 1971 ਵਿੱਚ ਬੰਗਲਾਦੇਸ਼ ਦੇ ਮੋਰਚੇ 'ਤੇ 4 ਸਿੱਖ ਨੇ ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਡੀ.ਐਸ. ਸਿੱਧੂ ਦੀ ਅਗਵਾਈ ਵਿੱਚ ਖੁਲਨਾ ਨੇੜੇ ਸਿਰਮਾਨੀ ਦੇ ਮਜ਼ਬੂਤ ਕਿਲ੍ਹੇ 'ਤੇ ਹਮਲਾ ਕੀਤਾ। ਦੁਸ਼ਮਣ ਦੇ ਕੰਕਰੀਟ ਬੰਕਰਾਂ ਅਤੇ ਟੈਂਕਾਂ ਦੇ ਬਾਵਜੂਦ ਸਿੱਖਾਂ ਨੇ ਦਲਦਲੀ ਜ਼ਮੀਨ 'ਤੇ ਸੰਗੀਨਾਂ ਨਾਲ ਜ਼ਬਰਦਸਤ ਹਮਲਾ ਬੋਲਿਆ ਅਤੇ ਪਾਕਿਸਤਾਨੀ ਫੌਜ ਨੂੰ ਆਤਮ-ਸਮਰਪਣ ਕਰਨ ਲਈ ਮਜਬੂਰ ਕੀਤਾ।"
    },
    {
        "art_num": 417,
        "title_en": "Kargil Operations (1999)",
        "title_hi": "कारगिल अभियान (1999)",
        "title_pa": "ਕਾਰਗਿਲ ਓਪਰੇਸ਼ਨਜ਼ (1999)",
        "year_en": "1999",
        "year_hi": "1999",
        "year_pa": "1999",
        "category_en": "Battle Gallery",
        "category_hi": "बैटल गैलरी",
        "category_pa": "ਬੈਟਲ ਗੈਲਰੀ",
        "regiment_en": "Sikh Regiment",
        "regiment_hi": "सिख रेजिमेंट",
        "regiment_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "summary_en": "In May to July 1999 during Operation Vijay in Kargil, 8 SIKH was inducted into the Dras and Batalik sub-sectors to capture formidable heights including Tiger Hill and Helmets. Scaling near-vertical icy cliffs at altitudes over 16,000 feet under relentless artillery and sniper fire, the Sikhs fought with superhuman grit. In savage hand-to-hand combat, they captured critical forward enemy footholds, suffering heavy casualties but isolating Tiger Hill and ensuring a historic Indian victory in Kargil.",
        "summary_hi": "मई-जुलाई 1999 में कारगिल में ऑपरेशन विजय के दौरान 8 सिख को द्रास और बटालिक सब-सेक्टरों में टाइगर हिल और हेलमेट्स जैसी दुर्गम चोटियों पर कब्जा करने का आदेश मिला। 16,000 फीट से अधिक की ऊंचाई पर बर्फीली सीधी चट्टानों पर चढ़ते हुए सिखों ने भीषण तोपखाने और स्नाइपर हमलों का सामना किया। आमने-सामने की खूनी लड़ाई में उन्होंने महत्वपूर्ण ठिकानों पर कब्जा किया और टाइगर हिल को अलग-थलग कर कारगिल में ऐतिहासिक विजय सुनिश्चित की।",
        "summary_pa": "ਮਈ-ਜੁਲਾਈ 1999 ਵਿੱਚ ਕਾਰਗਿਲ ਜੰਗ ਦੌਰਾਨ 8 ਸਿੱਖ ਨੇ ਦਰਾਸ ਅਤੇ ਬਟਾਲਿਕ ਸੈਕਟਰਾਂ ਵਿੱਚ ਟਾਈਗਰ ਹਿੱਲ ਅਤੇ ਹੈਲਮੇਟਸ ਵਰਗੀਆਂ ਉੱਚੀਆਂ ਚੋਟੀਆਂ 'ਤੇ ਹਮਲਾ ਕੀਤਾ। 16,000 ਫੁੱਟ ਤੋਂ ਵੱਧ ਉਚਾਈ 'ਤੇ ਬਰਫੀਲੀਆਂ ਚੱਟਾਨਾਂ ਚੜ੍ਹ ਕੇ ਸਿੱਖਾਂ ਨੇ ਭਾਰੀ ਗੋਲੀਬਾਰੀ ਦਰਮਿਆਨ ਆਹਮੋ-ਸਾਹਮਣੇ ਦੀ ਲੜਾਈ ਲੜੀ। ਭਾਰੀ ਕੁਰਬਾਨੀਆਂ ਦੇ ਕੇ ਦੁਸ਼ਮਣ ਦੇ ਪੈਰ ਉਖਾੜੇ ਅਤੇ ਕਾਰਗਿਲ ਵਿੱਚ ਇਤਿਹਾਸਕ ਜਿੱਤ ਦਰਜ ਕੀਤੀ।"
    }
]

def load_cache():
    if os.path.exists("translations_cache.json"):
        with open("translations_cache.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"hi": {}, "pa": {}}

CACHE = load_cache()

def save_cache():
    with open("translations_cache.json", "w", encoding="utf-8") as f:
        json.dump(CACHE, f, ensure_ascii=False, indent=2)

def trans_text(text, lang):
    t_str = str(text).strip()
    if not t_str or t_str.isdigit():
        return t_str
    if lang in CACHE and t_str in CACHE[lang]:
        return CACHE[lang][t_str]
    
    # If text is long, chunk by sentences or hard chunks
    if len(t_str) > 400:
        sentences = re.split(r'(?<=[.!?])\s+', t_str)
        if len(sentences) <= 1:
            # Hard chunk by word boundary around 300 chars
            words = t_str.split()
            sentences = []
            curr = []
            curr_len = 0
            for w in words:
                if curr_len + len(w) + 1 > 350:
                    sentences.append(" ".join(curr))
                    curr = [w]
                    curr_len = len(w)
                else:
                    curr.append(w)
                    curr_len += len(w) + 1
            if curr:
                sentences.append(" ".join(curr))
        
        translated_sentences = []
        for s in sentences:
            s_clean = s.strip()
            if not s_clean: continue
            if s_clean == t_str:
                # Direct fallback translate
                try:
                    res = GoogleTranslator(source='en', target=lang).translate(s_clean[:400])
                except Exception:
                    res = s_clean
                translated_sentences.append(res)
            else:
                translated_sentences.append(trans_text(s_clean, lang))
        res = " ".join(translated_sentences)
        CACHE.setdefault(lang, {})[t_str] = res
        return res

    for attempt in range(3):
        try:
            translator = GoogleTranslator(source='en', target=lang)
            res = translator.translate(t_str)
            if res:
                CACHE.setdefault(lang, {})[t_str] = res
                return res
        except Exception:
            pass
    
    return t_str

def update_html_pages():
    print("Updating English, Hindi, and Punjabi Battle Gallery HTML pages...", flush=True)
    total_pieces = len(BATTLES_DATA)
    
    for idx, item in enumerate(BATTLES_DATA):
        num = item["art_num"]
        prev_num = BATTLES_DATA[idx - 1]["art_num"] if idx > 0 else None
        next_num = BATTLES_DATA[idx + 1]["art_num"] if idx < total_pieces - 1 else None
        piece_idx = idx + 1
        
        # 1. Read base English HTML
        base_fn = f"art{num}.html"
        with open(base_fn, "r", encoding="utf-8") as f:
            soup_en = BeautifulSoup(f.read(), "html.parser")
        
        # Clean language switcher bar
        for b in soup_en.find_all("div", class_="lang-switch-bar"): b.decompose()
        
        # Ensure home link is index_en.html
        home_a_en = soup_en.find("a", href=re.compile(r"index.*\.html"))
        if home_a_en: home_a_en["href"] = "index_en.html"
        
        # Audio tag
        aud_en = soup_en.find("audio")
        if aud_en: aud_en["src"] = f"assets/audio/audio_{num}.mp3"
        
        # Navigation
        nav_en = soup_en.find("div", class_="navigation")
        if nav_en:
            prev_a = nav_en.find_all("a")[0] if len(nav_en.find_all("a")) > 0 else None
            next_a = nav_en.find_all("a")[1] if len(nav_en.find_all("a")) > 1 else None
            if prev_a:
                prev_a["href"] = f"art{prev_num}.html" if prev_num else "#"
                if not prev_num: prev_a["class"] = ["nav-link", "disabled"]
                else: prev_a["class"] = ["nav-link"]
            if next_a:
                next_a["href"] = f"art{next_num}.html" if next_num else "#"
                if not next_num: next_a["class"] = ["nav-link", "disabled"]
                else: next_a["class"] = ["nav-link"]
            span = nav_en.find("span")
            if span: span.string = f"Piece {piece_idx} / {total_pieces}"
        
        # Top Language Switcher Bar in EN
        en_switcher = BeautifulSoup(f"""
        <div class="lang-switch-bar" style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.85); padding: 8px 16px; border-radius: 14px; border: 1px solid var(--glass-border); margin-bottom: 20px; backdrop-filter: blur(12px);">
        <a class="nav-link" href="index.html" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.4); color: #cbd5e1;">
            🏛️ Language Portal
        </a>
        <div style="display: flex; gap: 8px; align-items: center;">
        <a class="nav-link" href="art{num}.html" style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24;">🇬🇧 English</a>
        <a class="nav-link" href="art{num}_hi.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇮🇳 हिन्दी</a>
        <a class="nav-link" href="art{num}_pa.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">ੴ ਪੰਜਾਬੀ</a>
        </div>
        </div>
        """, "html.parser")
        
        cont_en = soup_en.find("div", class_="gallery-container") or soup_en.find("body")
        if cont_en: cont_en.insert(0, en_switcher)
        
        with open(base_fn, "w", encoding="utf-8") as f:
            f.write(str(soup_en))
            
        # 2. Build Hindi Page
        soup_hi = BeautifulSoup(str(soup_en), "html.parser")
        for b in soup_hi.find_all("div", class_="lang-switch-bar"): b.decompose()
        
        hi_switcher = BeautifulSoup(f"""
        <div class="lang-switch-bar" style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.85); padding: 8px 16px; border-radius: 14px; border: 1px solid var(--glass-border); margin-bottom: 20px; backdrop-filter: blur(12px);">
        <a class="nav-link" href="index.html" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.4); color: #cbd5e1;">
            🏛️ भाषा चयन
        </a>
        <div style="display: flex; gap: 8px; align-items: center;">
        <a class="nav-link" href="art{num}.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇬🇧 English</a>
        <a class="nav-link" href="art{num}_hi.html" style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24;">🇮🇳 हिन्दी</a>
        <a class="nav-link" href="art{num}_pa.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">ੴ ਪੰਜਾਬੀ</a>
        </div>
        </div>
        """, "html.parser")
        cont_hi = soup_hi.find("div", class_="gallery-container") or soup_hi.find("body")
        if cont_hi: cont_hi.insert(0, hi_switcher)
        
        if soup_hi.find("title"): soup_hi.find("title").string = f"{item['title_hi']} - विरासत संग्रहालय"
        if soup_hi.find("h1"): soup_hi.find("h1").string = item["title_hi"]
        
        home_a_hi = soup_hi.find("a", href=re.compile(r"index.*\.html"))
        if home_a_hi:
            home_a_hi["href"] = "index_hi.html"
            for t in list(home_a_hi.find_all(string=True)):
                if "Back to Home" in t: t.replace_with(" मुख्य पृष्ठ")
        
        # Scroller section heading
        h2_hi = soup_hi.find("h2")
        if h2_hi and "BATTLE GALLERY PICTURES" in h2_hi.text:
            h2_hi.string = "बैटल गैलरी चित्र"
            
        # Translate scroller nomenclatures
        scroller_hi = soup_hi.find("div", class_="scroller-track")
        if scroller_hi:
            for nom in scroller_hi.find_all("div", class_="nomenclature"):
                txt = nom.text.strip()
                if txt:
                    nom.string = trans_text(txt, "hi")
                    
        # Audio Section
        aud_hi = soup_hi.find("audio")
        if aud_hi: aud_hi["src"] = f"assets/audio_hi/audio_{num}.mp3"
        play_btn_hi = soup_hi.find("button", class_="play-btn")
        if play_btn_hi:
            play_btn_hi.clear()
            play_btn_hi.append(BeautifulSoup('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg> वर्णन सुनें', 'html.parser'))
            
        # Description Boxes
        boxes_hi = soup_hi.find_all("div", class_="description-box")
        if len(boxes_hi) > 0:
            meta_html = f"""<strong>शीर्षक:</strong> {item['title_hi']}<br/>
<strong>श्रेणी:</strong> {item['category_hi']}<br/>
<strong>रेजिमेंट:</strong> {item['regiment_hi']}<br/>"""
            boxes_hi[0].clear()
            boxes_hi[0].append(BeautifulSoup(meta_html, "html.parser"))
            
        if len(boxes_hi) > 1:
            body_box_en = soup_en.find_all("div", class_="description-box")[1]
            paras_hi = []
            for p_tag in body_box_en.find_all("p"):
                p_txt = p_tag.get_text().strip()
                if p_txt:
                    paras_hi.append(f"<p>{trans_text(p_txt, 'hi')}</p>")
            if paras_hi:
                boxes_hi[1].clear()
                boxes_hi[1].append(BeautifulSoup("\n".join(paras_hi), "html.parser"))
                
        # Navigation
        nav_hi = soup_hi.find("div", class_="navigation")
        if nav_hi:
            prev_a = nav_hi.find_all("a")[0] if len(nav_hi.find_all("a")) > 0 else None
            next_a = nav_hi.find_all("a")[1] if len(nav_hi.find_all("a")) > 1 else None
            if prev_a:
                prev_a["href"] = f"art{prev_num}_hi.html" if prev_num else "#"
                if not prev_num: prev_a["class"] = ["nav-link", "disabled"]
                else: prev_a["class"] = ["nav-link"]
                prev_a.clear()
                prev_a.append(BeautifulSoup('<svg fill="none" height="20" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" width="20"><path d="M19 12H5M12 19l-7-7 7-7"></path></svg> पिछली कलाकृति', 'html.parser'))
            if next_a:
                next_a["href"] = f"art{next_num}_hi.html" if next_num else "#"
                if not next_num: next_a["class"] = ["nav-link", "disabled"]
                else: next_a["class"] = ["nav-link"]
                next_a.clear()
                next_a.append(BeautifulSoup('अगली कलाकृति <svg fill="none" height="20" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" width="20"><path d="M5 12h14M12 5l7 7-7 7"></path></svg>', 'html.parser'))
            span = nav_hi.find("span")
            if span: span.string = f"कलाकृति {piece_idx} / {total_pieces}"
            
        # QR Code Section
        qr_hi = soup_hi.find("div", class_="qr-info")
        if qr_hi:
            h3 = qr_hi.find("h3")
            p = qr_hi.find("p")
            if h3: h3.string = "मोबाइल पर खोलें"
            if p: p.string = "अपने फोन पर इस कलाकृति को देखने के लिए स्कैन करें।"
            
        # Script tags
        s_hi = soup_hi.find("script")
        if s_hi and s_hi.string:
            s_str = s_hi.string.replace("Pause Audio", "ऑडियो रोकें").replace("Listen to Narration", "वर्णन सुनें")
            s_hi.string = s_str
            
        with open(f"art{num}_hi.html", "w", encoding="utf-8") as f:
            f.write(str(soup_hi))
            
        # 3. Build Punjabi Page
        soup_pa = BeautifulSoup(str(soup_en), "html.parser")
        for b in soup_pa.find_all("div", class_="lang-switch-bar"): b.decompose()
        
        pa_switcher = BeautifulSoup(f"""
        <div class="lang-switch-bar" style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.85); padding: 8px 16px; border-radius: 14px; border: 1px solid var(--glass-border); margin-bottom: 20px; backdrop-filter: blur(12px);">
        <a class="nav-link" href="index.html" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.4); color: #cbd5e1;">
            🏛️ ਭਾਸ਼ਾ ਚੋਣ
        </a>
        <div style="display: flex; gap: 8px; align-items: center;">
        <a class="nav-link" href="art{num}.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇬🇧 English</a>
        <a class="nav-link" href="art{num}_hi.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇮🇳 हिन्दी</a>
        <a class="nav-link" href="art{num}_pa.html" style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24;">ੴ ਪੰਜਾਬੀ</a>
        </div>
        </div>
        """, "html.parser")
        cont_pa = soup_pa.find("div", class_="gallery-container") or soup_pa.find("body")
        if cont_pa: cont_pa.insert(0, pa_switcher)
        
        if soup_pa.find("title"): soup_pa.find("title").string = f"{item['title_pa']} - ਵਿਰਾਸਤ ਅਜਾਇਬ ਘਰ"
        if soup_pa.find("h1"): soup_pa.find("h1").string = item["title_pa"]
        
        home_a_pa = soup_pa.find("a", href=re.compile(r"index.*\.html"))
        if home_a_pa:
            home_a_pa["href"] = "index_pa.html"
            for t in list(home_a_pa.find_all(string=True)):
                if "Back to Home" in t: t.replace_with(" ਮੁੱਖ ਪੰਨਾ")
        
        # Scroller section heading
        h2_pa = soup_pa.find("h2")
        if h2_pa and "BATTLE GALLERY PICTURES" in h2_pa.text:
            h2_pa.string = "ਬੈਟਲ ਗੈਲਰੀ ਤਸਵੀਰਾਂ"
            
        # Translate scroller nomenclatures
        scroller_pa = soup_pa.find("div", class_="scroller-track")
        if scroller_pa:
            for nom in scroller_pa.find_all("div", class_="nomenclature"):
                txt = nom.text.strip()
                if txt:
                    nom.string = trans_text(txt, "pa")
                    
        # Audio Section
        aud_pa = soup_pa.find("audio")
        if aud_pa: aud_pa["src"] = f"assets/audio_pa/audio_{num}.mp3"
        play_btn_pa = soup_pa.find("button", class_="play-btn")
        if play_btn_pa:
            play_btn_pa.clear()
            play_btn_pa.append(BeautifulSoup('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg> ਵੇਰਵਾ ਸੁਣੋ', 'html.parser'))
            
        # Description Boxes
        boxes_pa = soup_pa.find_all("div", class_="description-box")
        if len(boxes_pa) > 0:
            meta_html = f"""<strong>ਸਿਰਲੇਖ:</strong> {item['title_pa']}<br/>
<strong>ਸ਼੍ਰੇਣੀ:</strong> {item['category_pa']}<br/>
<strong>ਰੈਜੀਮੈਂਟ:</strong> {item['regiment_pa']}<br/>"""
            boxes_pa[0].clear()
            boxes_pa[0].append(BeautifulSoup(meta_html, "html.parser"))
            
        if len(boxes_pa) > 1:
            body_box_en = soup_en.find_all("div", class_="description-box")[1]
            paras_pa = []
            for p_tag in body_box_en.find_all("p"):
                p_txt = p_tag.get_text().strip()
                if p_txt:
                    paras_pa.append(f"<p>{trans_text(p_txt, 'pa')}</p>")
            if paras_pa:
                boxes_pa[1].clear()
                boxes_pa[1].append(BeautifulSoup("\n".join(paras_pa), "html.parser"))
                
        # Navigation
        nav_pa = soup_pa.find("div", class_="navigation")
        if nav_pa:
            prev_a = nav_pa.find_all("a")[0] if len(nav_pa.find_all("a")) > 0 else None
            next_a = nav_pa.find_all("a")[1] if len(nav_pa.find_all("a")) > 1 else None
            if prev_a:
                prev_a["href"] = f"art{prev_num}_pa.html" if prev_num else "#"
                if not prev_num: prev_a["class"] = ["nav-link", "disabled"]
                else: prev_a["class"] = ["nav-link"]
                prev_a.clear()
                prev_a.append(BeautifulSoup('<svg fill="none" height="20" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" width="20"><path d="M19 12H5M12 19l-7-7 7-7"></path></svg> ਪਿਛਲੀ ਕਲਾਕ੍ਰਿਤੀ', 'html.parser'))
            if next_a:
                next_a["href"] = f"art{next_num}_pa.html" if next_num else "#"
                if not next_num: next_a["class"] = ["nav-link", "disabled"]
                else: next_a["class"] = ["nav-link"]
                next_a.clear()
                next_a.append(BeautifulSoup('ਅਗਲੀ ਕਲਾਕ੍ਰਿਤੀ <svg fill="none" height="20" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" width="20"><path d="M5 12h14M12 5l7 7-7 7"></path></svg>', 'html.parser'))
            span = nav_pa.find("span")
            if span: span.string = f"ਕਲਾਕ੍ਰਿਤੀ {piece_idx} / {total_pieces}"
            
        # QR Code Section
        qr_pa = soup_pa.find("div", class_="qr-info")
        if qr_pa:
            h3 = qr_pa.find("h3")
            p = qr_pa.find("p")
            if h3: h3.string = "ਮੋਬਾਈਲ 'ਤੇ ਖੋਲ੍ਹੋ"
            if p: p.string = "ਆਪਣੇ ਫ਼ੋਨ 'ਤੇ ਇਸ ਕਲਾ ਰਿਕਾਰਡ ਨੂੰ ਦੇਖਣ ਲਈ ਸਕੈਨ ਕਰੋ।"
            
        # Script tags
        s_pa = soup_pa.find("script")
        if s_pa and s_pa.string:
            s_str = s_pa.string.replace("Pause Audio", "ਆਡੀਓ ਰੋਕੋ").replace("Listen to Narration", "ਵੇਰਵਾ ਸੁਣੋ")
            s_pa.string = s_str
            
        with open(f"art{num}_pa.html", "w", encoding="utf-8") as f:
            f.write(str(soup_pa))

    save_cache()
    print("All 54 Battle Gallery HTML pages generated successfully!", flush=True)

def update_index_dropdowns():
    print("Updating Battle Gallery dropdown links in index_en.html, index_hi.html, index_pa.html...", flush=True)
    
    # 1. index_en.html
    with open("index_en.html", "r", encoding="utf-8") as f:
        soup_en = BeautifulSoup(f.read(), "html.parser")
    drop_en = soup_en.find("div", id="dropdown-5")
    if drop_en:
        drop_en.clear()
        for item in BATTLES_DATA:
            a_tag = soup_en.new_tag("a", href=f"art{item['art_num']}.html")
            a_tag.string = item["title_en"]
            drop_en.append(a_tag)
            drop_en.append("\n")
    with open("index_en.html", "w", encoding="utf-8") as f:
        f.write(str(soup_en))

    # 2. index_hi.html
    with open("index_hi.html", "r", encoding="utf-8") as f:
        soup_hi = BeautifulSoup(f.read(), "html.parser")
    drop_hi = soup_hi.find("div", id="dropdown-5")
    if drop_hi:
        drop_hi.clear()
        for item in BATTLES_DATA:
            a_tag = soup_hi.new_tag("a", href=f"art{item['art_num']}_hi.html")
            a_tag.string = item["title_hi"]
            drop_hi.append(a_tag)
            drop_hi.append("\n")
    with open("index_hi.html", "w", encoding="utf-8") as f:
        f.write(str(soup_hi))

    # 3. index_pa.html
    with open("index_pa.html", "r", encoding="utf-8") as f:
        soup_pa = BeautifulSoup(f.read(), "html.parser")
    drop_pa = soup_pa.find("div", id="dropdown-5")
    if drop_pa:
        drop_pa.clear()
        for item in BATTLES_DATA:
            a_tag = soup_pa.new_tag("a", href=f"art{item['art_num']}_pa.html")
            a_tag.string = item["title_pa"]
            drop_pa.append(a_tag)
            drop_pa.append("\n")
    with open("index_pa.html", "w", encoding="utf-8") as f:
        f.write(str(soup_pa))

async def synthesize_audio():
    print("Synthesizing 100-word smart audio recitations in English, Hindi, and Punjabi...", flush=True)
    os.makedirs("assets/audio", exist_ok=True)
    os.makedirs("assets/audio_hi", exist_ok=True)
    os.makedirs("assets/audio_pa", exist_ok=True)
    
    sem = asyncio.Semaphore(5)

    async def gen_en(num, text, title):
        speech_text = f"{title}. {text}"
        p = f"assets/audio/audio_{num}.mp3"
        async with sem:
            try:
                comm = edge_tts.Communicate(speech_text, 'en-IN-PrabhatNeural')
                await comm.save(p)
            except Exception as e:
                print(f"Fallback gTTS for EN art{num}: {e}")
                tts = gTTS(speech_text, lang='en')
                tts.save(p)

    async def gen_hi(num, text, title):
        speech_text = f"{title}. {text}"
        p = f"assets/audio_hi/audio_{num}.mp3"
        async with sem:
            try:
                comm = edge_tts.Communicate(speech_text, 'hi-IN-MadhurNeural')
                await comm.save(p)
            except Exception as e:
                print(f"Fallback gTTS for HI art{num}: {e}")
                tts = gTTS(speech_text, lang='hi')
                tts.save(p)

    tasks = []
    for item in BATTLES_DATA:
        num = item["art_num"]
        tasks.append(gen_en(num, item["summary_en"], item["title_en"]))
        tasks.append(gen_hi(num, item["summary_hi"], item["title_hi"]))
        
    await asyncio.gather(*tasks)
    print("English and Hindi audio synthesized successfully!", flush=True)

    print("Synthesizing Punjabi audio recitations via gTTS...", flush=True)
    for idx, item in enumerate(BATTLES_DATA, 1):
        num = item["art_num"]
        p = f"assets/audio_pa/audio_{num}.mp3"
        speech_text = f"{item['title_pa']}। {item['summary_pa']}"
        try:
            tts = gTTS(speech_text, lang='pa')
            tts.save(p)
            print(f"[{idx}/18] Punjabi audio generated for art{num}")
        except Exception as e:
            print(f"Error generating PA art{num}: {e}")

def main():
    print("=== STARTING BATTLE GALLERY OVERHAUL ===", flush=True)
    update_html_pages()
    update_index_dropdowns()
    asyncio.run(synthesize_audio())
    print("=== BATTLE GALLERY OVERHAUL COMPLETED SUCCESSFULLY! ===", flush=True)

if __name__ == "__main__":
    main()
