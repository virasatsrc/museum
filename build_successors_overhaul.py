import os, sys, re, json, asyncio
from bs4 import BeautifulSoup
import edge_tts
from gtts import gTTS
from deep_translator import GoogleTranslator

SUCCESSORS_DATA = [
    {
        "num": 601,
        "title_en": "XIV Ferozepore Sikhs",
        "title_hi": "14वीं फिरोजपुर सिख",
        "title_pa": "14ਵੀਂ ਫਿਰੋਜ਼ਪੁਰ ਸਿੱਖ",
        "category_en": "Successor Battalions",
        "category_hi": "उत्तराधिकारी बटालियनें",
        "category_pa": "ਉੱਤਰਾਧਿਕਾਰੀ ਬਟਾਲੀਅਨਾਂ",
        "summary_en": "Raised on July 30, 1846, at Ferozepore by Captain G. Tebbs, the XIV Ferozepore Sikhs (now 1 SIKH / 4 MECH INF) was formed from disbanded soldiers of the Khalsa Army. Commanded by Major J. Brasyer, the regiment established its reputation for unmatched valor during the 1857 Siege of Arrah and Lucknow. Over decades of illustrious service, the battalion fought across the North-West Frontier, China, and in World War I at the historic Battle of Gallipoli (1915). In 1947, 1 Sikh spearheaded the critical airlanding at Srinagar, saving the Kashmir Valley and earning legendary fame.",
        "summary_hi": "14वीं फिरोजपुर सिख (वर्तमान 1 सिख / 4 मैक इन्फैंट्री) की स्थापना 30 जुलाई 1846 को कैप्टन जी. टेब्स द्वारा फिरोजपुर में की गई थी। खालसा सेना के पूर्व सैनिकों से गठित इस बटालियन ने 1857 के आरा और लखनऊ के घेराव में अद्वितीय वीरता का परिचय दिया। बटालियन ने उत्तर-पश्चिम सीमांत, चीन और प्रथम विश्व युद्ध में ऐतिहासिक गैलीपोली की लड़ाई (1915) में अदम्य साहस दिखाया। अक्टूबर 1947 में 1 सिख ने श्रीनगर हवाई अड्डे पर ऐतिहासिक एयरलैंडिंग कर कश्मीर घाटी को आक्रमणकारियों से बचाया और भारतीय सैन्य इतिहास में अमर कीर्ति प्राप्त की।",
        "summary_pa": "14ਵੀਂ ਫਿਰੋਜ਼ਪੁਰ ਸਿੱਖ (ਹੁਣ 1 ਸਿੱਖ / 4 ਮੈਕ ਇਨਫੈਂਟਰੀ) ਦੀ ਸਥਾਪਨਾ 30 ਜੁਲਾਈ 1846 ਨੂੰ ਫਿਰੋਜ਼ਪੁਰ ਵਿਖੇ ਕੈਪਟਨ ਜੀ. ਟੈਬਸ ਦੁਆਰਾ ਕੀਤੀ ਗਈ ਸੀ। ਖਾਲਸਾ ਫੌਜ ਦੇ ਬਹਾਦਰ ਜਵਾਨਾਂ ਤੋਂ ਬਣੀ ਇਸ ਬਟਾਲੀਅਨ ਨੇ 1857 ਵਿੱਚ ਆਰਾ ਅਤੇ ਲਖਨਊ ਵਿਖੇ ਬੇਮਿਸਾਲ ਦਲੇਰੀ ਦਿਖਾਈ। ਬਟਾਲੀਅਨ ਨੇ ਉੱਤਰ-ਪੱਛਮੀ ਸਰਹੱਦ, ਚੀਨ ਅਤੇ ਪਹਿਲੇ ਵਿਸ਼ਵ ਯੁੱਧ ਦੌਰਾਨ ਗੈਲੀਪੋਲੀ ਦੀ ਲੜਾਈ (1915) ਵਿੱਚ ਵੱਡੀ ਸ਼ਹਾਦਤ ਦਿੱਤੀ। ਅਕਤੂਬਰ 1947 ਵਿੱਚ 1 ਸਿੱਖ ਨੇ ਸ੍ਰੀਨਗਰ ਵਿਖੇ ਇਤਿਹਾਸਕ ਏਅਰਲੈਂਡਿੰਗ ਕਰਕੇ ਕਸ਼ਮੀਰ ਵਾਦੀ ਨੂੰ ਬਚਾਇਆ ਅਤੇ ਅਮਿੱਟ ਸ਼ਾਨ ਹਾਸਲ ਕੀਤੀ।"
    },
    {
        "num": 602,
        "title_en": "XV Ludhiana Sikhs",
        "title_hi": "15वीं लुधियाना सिख",
        "title_pa": "15ਵੀਂ ਲੁਧਿਆਣਾ ਸਿੱਖ",
        "category_en": "Successor Battalions",
        "category_hi": "उत्तराधिकारी बटालियनें",
        "category_pa": "ਉੱਤਰਾਧਿਕਾਰੀ ਬਟਾਲੀਅਨਾਂ",
        "summary_en": "Formed on August 1, 1846, by Major P. Gordon, the XV Ludhiana Sikhs (now 2 SIKH) drew battle-hardened Khalsa veterans from Punjab's Malwa and Majha regions. Renowned for discipline, physical prowess, and martial spirit, the battalion saw extensive action in the Second Anglo-Burmese War, China, the Sudan Campaign at Tofrek (1885), and the North-West Frontier. During World War I, 2 Sikh fought gallantly in France at Neuve Chapelle and in Mesopotamia. Known as the 'Bravest of the Brave', 2 Sikh continues to be one of the most decorated infantry battalions in the Indian Army.",
        "summary_hi": "15वीं लुधियाना सिख (वर्तमान 2 सिख) की स्थापना 1 अगस्त 1846 को मेजर पी. गॉर्डन द्वारा की गई थी। पंजाब के मालवा और माझा क्षेत्र के खालसा योद्धाओं से सजी इस बटालियन ने द्वितीय आंग्ल-बर्मा युद्ध, चीन, सूडान में टोफ्रेक की लड़ाई (1885) और उत्तर-पश्चिम सीमांत पर अदम्य पराक्रम दिखाया। प्रथम विश्व युद्ध के दौरान 2 सिख ने फ्रांस के न्यूव शापेल और मेसोपोटामिया में ऐतिहासिक वीरता का प्रदर्शन किया। 'ब्रेवेस्ट ऑफ द ब्रेव' के खिताब से सम्मानित 2 सिख भारतीय सेना की सर्वाधिक पदक विजेता बटालियनों में शुमार है।",
        "summary_pa": "15ਵੀਂ ਲੁਧਿਆਣਾ ਸਿੱਖ (ਹੁਣ 2 ਸਿੱਖ) ਦੀ ਸਥਾਪਨਾ 1 ਅਗਸਤ 1846 ਨੂੰ ਮੇਜਰ ਪੀ. ਗਾਰਡਨ ਦੁਆਰਾ ਕੀਤੀ ਗਈ ਸੀ। ਮਾਲਵਾ ਅਤੇ ਮਾਝਾ ਦੇ ਖਾਲਸਾ ਸੂਰਬੀਰਾਂ ਨਾਲ ਸਜੀ ਇਸ ਬਟਾਲੀਅਨ ਨੇ ਦੂਜੇ ਬਰਮਾ ਯੁੱਧ, ਚੀਨ, ਸੁਡਾਨ ਵਿੱਚ ਟੋਫਰੇਕ ਦੀ ਲੜਾਈ (1885) ਅਤੇ ਉੱਤਰ-ਪੱਛਮੀ ਸਰਹੱਦ 'ਤੇ ਸ਼ਾਨਦਾਰ ਬਹਾਦਰੀ ਦਿਖਾਈ। ਪਹਿਲੇ ਵਿਸ਼ਵ ਯੁੱਧ ਵਿੱਚ 2 ਸਿੱਖ ਨੇ ਫਰਾਂਸ ਦੇ ਨਿਊਵ ਚਪੇਲ ਅਤੇ ਮੇਸੋਪੋਟੇਮੀਆ ਵਿੱਚ ਦਲੇਰੀ ਨਾਲ ਦੁਸ਼ਮਣ ਦੇ ਛੱਕੇ ਛੁਡਾਏ। 'ਬਹਾਦਰਾਂ ਵਿੱਚੋਂ ਸਭ ਤੋਂ ਬਹਾਦਰ' ਕਹੀ ਜਾਣ ਵਾਲੀ 2 ਸਿੱਖ ਫੌਜ ਦੀਆਂ ਸਭ ਤੋਂ ਵੱਧ ਸਨਮਾਨਿਤ ਬਟਾਲੀਅਨਾਂ ਵਿੱਚੋਂ ਇੱਕ ਹੈ।"
    },
    {
        "num": 603,
        "title_en": "XLV Rattray's Sikhs",
        "title_hi": "45वीं रैट्रेज़ सिख",
        "title_pa": "45ਵੀਂ ਰੈਟਰੇਜ਼ ਸਿੱਖ",
        "category_en": "Successor Battalions",
        "category_hi": "उत्तराधिकारी बटालियनें",
        "category_pa": "ਉੱਤਰਾਧਿਕਾਰੀ ਬਟਾਲੀਅਨਾਂ",
        "summary_en": "Raised on January 31, 1856, at Lahore by Captain Thomas Rattray, the XLV Rattray’s Sikhs (now 3 SIKH) originated as the elite Bengal Military Police Battalion. Distinguishing itself during the 1857 uprisings in Bihar, the unit was integrated into the line infantry in 1864. The battalion earned legendary battle honors in the Afghan Wars, the Malakand operations (1897), and Tirah Campaign. In World War I, 3 Sikh served heroically in Mesopotamia at the Battle of Hai (1917), earning the Victoria Cross. Today, 3 Sikh stands tall as a beacon of indomitable courage and steadfast loyalty.",
        "summary_hi": "45वीं रैट्रेज़ सिख (वर्तमान 3 सिख) की स्थापना 31 जनवरी 1856 को लाहौर में कैप्टन थॉमस रैट्रे द्वारा की गई थी। प्रारंभ में बंगाल सैन्य पुलिस बटालियन के रूप में गठित इस यूनिट ने 1857 के बिहार अभियानों में अद्वितीय पराक्रम दिखाया और 1864 में नियमित पैदल सेना में शामिल हुई। बटालियन ने अफगान युद्धों, मलकंद (1897) और तीराह अभियानों में असाधारण ख्याति अर्जित की। प्रथम विश्व युद्ध के दौरान 1917 में मेसोपोटामिया में हाई की लड़ाई में 3 सिख ने सर्वोच्च वीरता दिखाते हुए विक्टोरिया क्रॉस जीता।",
        "summary_pa": "45ਵੀਂ ਰੈਟਰੇਜ਼ ਸਿੱਖ (ਹੁਣ 3 ਸਿੱਖ) ਦੀ ਸਥਾਪਨਾ 31 ਜਨਵਰੀ 1856 ਨੂੰ ਲਾਹੌਰ ਵਿਖੇ ਕੈਪਟਨ ਥਾਮਸ ਰੈਟਰੇ ਦੁਆਰਾ ਕੀਤੀ ਗਈ ਸੀ। 1857 ਵਿੱਚ ਬਿਹਾਰ ਦੀਆਂ ਮੁਹਿੰਮਾਂ ਵਿੱਚ ਵੱਡੀ ਬਹਾਦਰੀ ਦਿਖਾਉਣ ਤੋਂ ਬਾਅਦ 1864 ਵਿੱਚ ਇਸਨੂੰ ਰੈਗੂਲਰ ਇਨਫੈਂਟਰੀ ਬਣਾਇਆ ਗਿਆ। ਬਟਾਲੀਅਨ ਨੇ ਅਫਗਾਨ ਯੁੱਧਾਂ, ਮਲਕੰਦ (1897) ਅਤੇ ਤੀਰਾਹ ਮੁਹਿੰਮ ਵਿੱਚ ਵੱਡੇ ਜੰਗੀ ਸਨਮਾਨ ਜਿੱਤੇ। ਪਹਿਲੇ ਵਿਸ਼ਵ ਯੁੱਧ ਵਿੱਚ 1917 ਵਿੱਚ ਮੇਸੋਪੋਟੇਮੀਆ ਦੀ ਹਾਈ ਲੜਾਈ ਦੌਰਾਨ 3 ਸਿੱਖ ਨੇ ਅਦੁੱਤੀ ਵੀਰਤਾ ਦਿਖਾਉਂਦਿਆਂ ਵਿਕਟੋਰੀਆ ਕਰਾਸ ਹਾਸਲ ਕੀਤਾ।"
    },
    {
        "num": 604,
        "title_en": "XXXV Sikhs",
        "title_hi": "35वीं सिख",
        "title_pa": "35ਵੀਂ ਸਿੱਖ",
        "category_en": "Successor Battalions",
        "category_hi": "उत्तराधिकारी बटालियनें",
        "category_pa": "ਉੱਤਰਾਧਿਕਾਰੀ ਬਟਾਲੀਅਨਾਂ",
        "summary_en": "Raised on April 29, 1887, at Ferozepore by Lieutenant Colonel D.W. Inglish, the XXXV Sikhs was formed exclusively of Jat Sikhs from north of the Sutlej. Deploying to Nyasaland (modern Malawi) in Central Africa (1893–1895), the battalion suppressed slave-trading insurgencies and established lasting peace. It fought with great distinction in the Malakand operations (1897) and the Third Afghan War (1919). In the 1922 reorganisation, 35 Sikhs became the 10th (Training) Battalion of the 11th Sikh Regiment, ultimately evolving into the prestigious Sikh Regimental Centre (SRC), the foundational training cradle of all Sikh Regiment soldiers.",
        "summary_hi": "35वीं सिख की स्थापना 29 अप्रैल 1887 को फिरोजपुर में लेफ्टिनेंट कर्नल डी.डब्ल्यू. इंगलिश द्वारा की गई थी। सतलुज पार के जाट सिखों से सजी इस बटालियन ने मध्य अफ्रीका के न्यासालैंड (मलावी) में 1893 से 1895 तक दास-व्यापार विरोधी अभियानों में शांति स्थापित की। इसने मलकंद (1897) और तृतीय अफगान युद्ध (1919) में विशिष्ट वीरता दिखाई। 1922 के सेना पुनर्गठन में यह 11वीं सिख रेजिमेंट की 10वीं (प्रशिक्षण) बटालियन बनी, जो कालांतर में प्रतिष्ठित सिख रेजिमेंटल सेंटर (SRC) के रूप में विकसित हुई, जहां सभी सिख सैनिकों को सैन्य प्रशिक्षण दिया जाता है।",
        "summary_pa": "35ਵੀਂ ਸਿੱਖ ਦੀ ਸਥਾਪਨਾ 29 ਅਪ੍ਰੈਲ 1887 ਨੂੰ ਫਿਰੋਜ਼ਪੁਰ ਵਿਖੇ ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਡੀ.ਡਬਲਿਊ. ਇੰਗਲਿਸ਼ ਦੁਆਰਾ ਕੀਤੀ ਗਈ ਸੀ। ਸਤਲੁਜੋਂ ਪਾਰ ਦੇ ਜੱਟ ਸਿੱਖਾਂ ਤੋਂ ਬਣੀ ਇਸ ਬਟਾਲੀਅਨ ਨੇ ਅਫਰੀਕਾ ਦੇ ਨਿਆਸਾਲੈਂਡ (ਮਲਾਵੀ) ਵਿੱਚ ਗੁਲਾਮਾਂ ਦੇ ਵਪਾਰੀਆਂ ਵਿਰੁੱਧ ਸਫਲ ਮੁਹਿੰਮ ਚਲਾਈ। ਇਸਨੇ ਮਲਕੰਦ (1897) ਅਤੇ ਤੀਜੀ ਅਫਗਾਨ ਜੰਗ (1919) ਵਿੱਚ ਬਹਾਦਰੀ ਦਿਖਾਈ। 1922 ਦੇ ਪੁਨਰਗਠਨ ਵਿੱਚ ਇਹ 10ਵੀਂ ਸਿਖਲਾਈ ਬਟਾਲੀਅਨ ਬਣੀ, ਜੋ ਬਾਅਦ ਵਿੱਚ ਮਹਾਨ ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਵਜੋਂ ਵਿਕਸਤ ਹੋਈ।"
    },
    {
        "num": 605,
        "title_en": "Re-organisation of the Indian Army (1922)",
        "title_hi": "भारतीय सेना का पुनर्गठन (1922)",
        "title_pa": "ਭਾਰਤੀ ਫੌਜ ਦਾ ਪੁਨਰਗਠਨ (1922)",
        "category_en": "Successor Battalions",
        "category_hi": "उत्तराधिकारी बटालियनें",
        "category_pa": "ਉੱਤਰਾਧਿਕਾਰੀ ਬਟਾਲੀਅਨਾਂ",
        "summary_en": "The landmark 1922 Indian Army Re-organisation fundamentally transformed the military system based on First World War experience. Disparate single-battalion Sikh units were unified into the single, permanent '11th Sikh Regiment'. The historic battalions were renumbered: 14th Sikhs became 1/11 Sikh, 15th Sikhs became 2/11 Sikh, 45th Rattray’s became 3/11 Sikh, 36th Sikhs became 4/11 Sikh, 47th Sikhs became 5/11 Sikh, and 35th Sikhs became the 10/11 Sikh Training Battalion (now SRC). This unified structure created common regimental heritage, streamlined recruitment, standardized training, and built the formidable modern identity of the Sikh Regiment.",
        "summary_hi": "1922 का भारतीय सेना पुनर्गठन प्रथम विश्व युद्ध के अनुभवों पर आधारित एक ऐतिहासिक सुधार था। इसके तहत विभिन्न एकल-बटालियन सिख इकाइयों को एक स्थायी '11वीं सिख रेजिमेंट' में एकीकृत किया गया। ऐतिहासिक बटालियनों को नया स्वरूप दिया गया: 14वीं सिख बनी 1/11 सिख, 15वीं सिख बनी 2/11 सिख, 45वीं रैट्रेज बनी 3/11 सिख, 36वीं सिख बनी 4/11 सिख, 47वीं सिख बनी 5/11 सिख तथा 35वीं सिख बनी 10/11 प्रशिक्षण बटालियन (वर्तमान एसआरसी)। इस पुनर्गठन ने सिख रेजिमेंट को एक साझा गौरवशाली पहचान और सुदृढ़ आधार प्रदान किया।",
        "summary_pa": "1922 ਦਾ ਭਾਰਤੀ ਫੌਜ ਦਾ ਪੁਨਰਗਠਨ ਪਹਿਲੇ ਵਿਸ਼ਵ ਯੁੱਧ ਦੇ ਸਬਕਾਂ 'ਤੇ ਆਧਾਰਿਤ ਇੱਕ ਇਨਕਲਾਬੀ ਕਦਮ ਸੀ। ਇਸ ਤਹਿਤ ਵੱਖ-ਵੱਖ ਸਿੱਖ ਬਟਾਲੀਅਨਾਂ ਨੂੰ ਇਕੱਠਾ ਕਰਕੇ '11ਵੀਂ ਸਿੱਖ ਰੈਜੀਮੈਂਟ' ਬਣਾਈ ਗਈ। ਇਤਿਹਾਸਕ ਬਟਾਲੀਅਨਾਂ ਨੂੰ ਨਵੇਂ ਨੰਬਰ ਦਿੱਤੇ ਗਏ: 14ਵੀਂ ਸਿੱਖ 1/11 ਸਿੱਖ ਬਣੀ, 15ਵੀਂ ਸਿੱਖ 2/11 ਸਿੱਖ, 45ਵੀਂ ਰੈਟਰੇਜ਼ 3/11 ਸਿੱਖ, 36ਵੀਂ ਸਿੱਖ 4/11 ਸਿੱਖ, 47ਵੀਂ ਸਿੱਖ 5/11 ਸਿੱਖ ਅਤੇ 35ਵੀਂ ਸਿੱਖ 10/11 ਟ੍ਰੇਨਿੰਗ ਬਟਾਲੀਅਨ (ਹੁਣ ਐਸਆਰਸੀ) ਬਣੀ। ਇਸਨੇ ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਨੂੰ ਇੱਕ ਸਾਂਝੀ ਸ਼ਾਨਦਾਰ ਪਛਾਣ ਦਿੱਤੀ।"
    },
    {
        "num": 606,
        "title_en": "XXXVI Sikhs",
        "title_hi": "36वीं सिख",
        "title_pa": "36ਵੀਂ ਸਿੱਖ",
        "category_en": "Successor Battalions",
        "category_hi": "उत्तराधिकारी बटालियनें",
        "category_pa": "ਉੱਤਰਾਧਿਕਾਰੀ ਬਟਾਲੀਅਨਾਂ",
        "summary_en": "Raised on March 23, 1887, at Jullundur by Lieutenant Colonel Jim Cooke, the XXXVI Sikhs (now 4 SIKH) is world-renowned for the epochal Battle of Saragarhi (12 September 1897). In that legendary stand, 21 brave Sikh soldiers under Havildar Ishar Singh fought to the last man and round against 10,000 Afghan tribesmen, all posthumously receiving the Indian Order of Merit. In World War I, 4 Sikh fought fiercely in the Siege of Tsingtao (1914), Gallipoli, and Mesopotamia, later winning the Battle of Barki in 1965. 4 Sikh remains an everlasting symbol of supreme valor.",
        "summary_hi": "36वीं सिख (वर्तमान 4 सिख) की स्थापना 23 मार्च 1887 को जालंधर में लेफ्टिनेंट कर्नल जिम कुक द्वारा की गई थी। यह बटालियन ऐतिहासिक सारागढ़ी के युद्ध (12 सितंबर 1897) के लिए विश्वविख्यात है, जहां हवलदार ईशर सिंह के नेतृत्व में 21 वीर सिख सैनिकों ने 10,000 अफगान हमलावरों के विरुद्ध अंतिम सांस और अंतिम गोली तक लड़ते हुए सर्वोच्च बलिदान दिया और सभी को मरणोपरांत इंडियन ऑर्डर ऑफ मेरिट मिला। प्रथम विश्व युद्ध में त्सिंगताओ, गैलीपोली और 1965 में बरकी की लड़ाई जीतकर 4 सिख ने अमर ख्याति प्राप्त की।",
        "summary_pa": "36ਵੀਂ ਸਿੱਖ (ਹੁਣ 4 ਸਿੱਖ) ਦੀ ਸਥਾਪਨਾ 23 ਮਾਰਚ 1887 ਨੂੰ ਜਲੰਧਰ ਵਿਖੇ ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਜਿਮ ਕੁੱਕ ਦੁਆਰਾ ਕੀਤੀ ਗਈ ਸੀ। ਇਹ ਬਟਾਲੀਅਨ ਇਤਿਹਾਸਕ ਸਾਰਾਗੜ੍ਹੀ ਦੀ ਜੰਗ (12 ਸਤੰਬਰ 1897) ਲਈ ਪੂਰੀ ਦੁਨੀਆ ਵਿੱਚ ਮਸ਼ਹੂਰ ਹੈ, ਜਿੱਥੇ ਹਵਾਲਦਾਰ ਈਸ਼ਰ ਸਿੰਘ ਦੀ ਅਗਵਾਈ ਵਿੱਚ 21 ਸਿੱਖ ਸੂਰਬੀਰਾਂ ਨੇ 10,000 ਅਫਗਾਨਾਂ ਦਾ ਮੁਕਾਬਲਾ ਕਰਦਿਆਂ ਸ਼ਹਾਦਤ ਪਾਈ ਅਤੇ ਸਾਰਿਆਂ ਨੂੰ ਆਈਓਐਮ ਮਿਲਿਆ। ਪਹਿਲੇ ਵਿਸ਼ਵ ਯੁੱਧ ਵਿੱਚ ਤਸਿੰਗਤਾਓ, ਗੈਲੀਪੋਲੀ ਅਤੇ 1965 ਵਿੱਚ ਬਾਰਕੀ ਜਿੱਤ ਕੇ 4 ਸਿੱਖ ਨੇ ਵੱਡਾ ਇਤਿਹਾਸ ਰਚਿਆ।"
    },
    {
        "num": 607,
        "title_en": "XLVII SIKHS",
        "title_hi": "47वीं सिख",
        "title_pa": "47ਵੀਂ ਸਿੱਖ",
        "category_en": "Successor Battalions",
        "category_hi": "उत्तराधिकारी बटालियनें",
        "category_pa": "ਉੱਤਰਾਧਿਕਾਰੀ ਬਟਾਲੀਅਨਾਂ",
        "summary_en": "Raised on January 22, 1901, at Sialkot as the 47th (Sikh) Regiment of Bengal Infantry by Major Percy Gerald Walker, XLVII SIKHS (now 5 SIKH) was the final pre-independence Sikh battalion raised. Earning the moniker 'The Storm Troopers of the Indian Army' during World War I, the battalion fought with immortal ferocity at Neuve Chapelle (1914), the Second Battle of Ypres (1915), and the Mesopotamia Campaign. In World War II, 5 Sikh fought tenaciously in Malaya and Burma. 5 Sikh continues its illustrious legacy as a vanguard of bravery in the Sikh Regiment.",
        "summary_hi": "47वीं सिख (वर्तमान 5 सिख) की स्थापना 22 जनवरी 1901 को सियालकोट में मेजर पर्सी गेराल्ड वॉकर द्वारा की गई थी। स्वतंत्रता-पूर्व सिख संदर्भ में गठित यह अंतिम बटालियन थी। प्रथम विश्व युद्ध के दौरान 'भारतीय सेना के स्टॉर्म ट्रूपर्स' के रूप में विख्यात इस बटालियन ने न्यूव शापेल (1914), यप्रेस की दूसरी लड़ाई (1915) और मेसोपोटामिया में अद्वितीय पराक्रम दिखाया। द्वितीय विश्व युद्ध में 5 सिख ने मलाया और बर्मा में बहादुरी से लड़ाई लड़ी। 5 सिख आज भी अदम्य वीरता और सर्वोच्च बलिदान का जीवंत प्रतीक है।",
        "summary_pa": "47ਵੀਂ ਸਿੱਖ (ਹੁਣ 5 ਸਿੱਖ) ਦੀ ਸਥਾਪਨਾ 22 ਜਨਵਰੀ 1901 ਨੂੰ ਸਿਆਲਕੋਟ ਵਿਖੇ ਮੇਜਰ ਪਰਸੀ ਗੇਰਾਲਡ ਵਾਕਰ ਦੁਆਰਾ ਕੀਤੀ ਗਈ ਸੀ। ਪਹਿਲੇ ਵਿਸ਼ਵ ਯੁੱਧ ਦੌਰਾਨ 'ਭਾਰਤੀ ਫੌਜ ਦੇ ਤੂਫਾਨੀ ਦਸਤੇ' (ਸਟੋਰਮ ਟਰੂਪਰਜ਼) ਵਜੋਂ ਜਾਣੀ ਜਾਂਦੀ ਇਸ ਬਟਾਲੀਅਨ ਨੇ ਨਿਊਵ ਚਪੇਲ (1914), ਇਪਰੇਸ (1915) ਅਤੇ ਮੇਸੋਪੋਟੇਮੀਆ ਵਿੱਚ ਲਾਸਾਨੀ ਬਹਾਦਰੀ ਦਿਖਾਈ। ਦੂਜੇ ਵਿਸ਼ਵ ਯੁੱਧ ਵਿੱਚ 5 ਸਿੱਖ ਨੇ ਮਲਾਇਆ ਅਤੇ ਬਰਮਾ ਵਿੱਚ ਦਲੇਰੀ ਨਾਲ ਲੜਾਈ ਲੜੀ। 5 ਸਿੱਖ ਅੱਜ ਵੀ ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦਾ ਮਾਣਮੱਤਾ ਥੰਮ੍ਹ ਹੈ।"
    }
]

# Scroller Captions Dictionaries for 605 and 607
CAPTIONS_605_HI = {
    "slide_106.webp": "नवंबर 1914 में उत्तरी फ्रांस में सिख जेसीओ के साथ फील्ड मार्शल फ्रेडरिक रॉबर्ट्स",
    "slide_107.webp": "नवंबर 1914 में उत्तरी फ्रांस में सिख जेसीओ के साथ फील्ड मार्शल फ्रेडरिक रॉबर्ट्स",
    "slide_108.webp": "नवंबर 1914 में उत्तरी फ्रांस में सिख जेसीओ के साथ फील्ड मार्शल फ्रेडरिक रॉबर्ट्स",
    "slide_109.webp": "नवंबर 1914 में उत्तरी फ्रांस में सिख जेसीओ के साथ फील्ड मार्शल फ्रेडरिक रॉबर्ट्स",
    "slide_110.webp": "नवंबर 1914 में उत्तरी फ्रांस में सिख जेसीओ के साथ फील्ड मार्शल फ्रेडरिक रॉबर्ट्स",
    "slide_111.webp": "नवंबर 1914 में उत्तरी फ्रांस में सिख जेसीओ के साथ फील्ड मार्शल फ्रेडरिक रॉबर्ट्स"
}
CAPTIONS_605_PA = {
    "slide_106.webp": "ਨਵੰਬਰ 1914 ਵਿੱਚ ਉੱਤਰੀ ਫਰਾਂਸ ਵਿੱਚ ਸਿੱਖ ਜੇਸੀਓਜ਼ ਨਾਲ ਫੀਲਡ ਮਾਰਸ਼ਲ ਫਰੈਡਰਿਕ ਰੌਬਰਟਸ",
    "slide_107.webp": "ਨਵੰਬਰ 1914 ਵਿੱਚ ਉੱਤਰੀ ਫਰਾਂਸ ਵਿੱਚ ਸਿੱਖ ਜੇਸੀਓਜ਼ ਨਾਲ ਫੀਲਡ ਮਾਰਸ਼ਲ ਫਰੈਡਰਿਕ ਰੌਬਰਟਸ",
    "slide_108.webp": "ਨਵੰਬਰ 1914 ਵਿੱਚ ਉੱਤਰੀ ਫਰਾਂਸ ਵਿੱਚ ਸਿੱਖ ਜੇਸੀਓਜ਼ ਨਾਲ ਫੀਲਡ ਮਾਰਸ਼ਲ ਫਰੈਡਰਿਕ ਰੌਬਰਟਸ",
    "slide_109.webp": "ਨਵੰਬਰ 1914 ਵਿੱਚ ਉੱਤਰੀ ਫਰਾਂਸ ਵਿੱਚ ਸਿੱਖ ਜੇਸੀਓਜ਼ ਨਾਲ ਫੀਲਡ ਮਾਰਸ਼ਲ ਫਰੈਡਰਿਕ ਰੌਬਰਟਸ",
    "slide_110.webp": "ਨਵੰਬਰ 1914 ਵਿੱਚ ਉੱਤਰੀ ਫਰਾਂਸ ਵਿੱਚ ਸਿੱਖ ਜੇਸੀਓਜ਼ ਨਾਲ ਫੀਲਡ ਮਾਰਸ਼ਲ ਫਰੈਡਰਿਕ ਰੌਬਰਟਸ",
    "slide_111.webp": "ਨਵੰਬਰ 1914 ਵਿੱਚ ਉੱਤਰੀ ਫਰਾਂਸ ਵਿੱਚ ਸਿੱਖ ਜੇਸੀਓਜ਼ ਨਾਲ ਫੀਲਡ ਮਾਰਸ਼ਲ ਫਰੈਡਰਿਕ ਰੌਬਰਟਸ"
}

CAPTIONS_607_HI = {
    "image6.webp": "मेसोपोटामिया के युद्ध में श्री गुरु ग्रंथ साहिब जी को शीश पर धारण कर आगे बढ़ते 47वीं सिख के वीर सैनिक",
    "image5.webp": "लेफ्टिनेंट कर्नल पर्सी गेराल्ड वॉकर, 47वीं सिख के प्रथम कमांडिंग ऑफिसर",
    "image3.webp": "47वीं सिख (ऐतिहासिक चित्र)",
    "image4.webp": "47वीं सिख का बेल्ट बकल",
    "image1.webp": "लेफ्टिनेंट कर्नल पर्सी गेराल्ड वॉकर, 47वीं सिख के प्रथम कमांडिंग ऑफिसर",
    "image2.webp": "विजय परेड: प्रथम विश्व युद्ध के बाद लंदन के पॉल मॉल में मार्च करते 47वीं सिख के वीर जवान और अधिकारी",
    "image7.webp": "बटालियन स्थापना के समय ब्रिटिश और भारतीय अधिकारी",
    "image8.webp": "5 सिख के गार्ड ऑफ ऑनर का निरीक्षण करते जनरल मुहम्मद मूसा"
}
CAPTIONS_607_PA = {
    "image6.webp": "ਮੇਸੋਪੋਟੇਮੀਆ ਦੀ ਜੰਗ ਵਿੱਚ ਸ੍ਰੀ ਗੁਰੂ ਗ੍ਰੰਥ ਸਾਹਿਬ ਜੀ ਨੂੰ ਸੀਸ 'ਤੇ ਸਜਾ ਕੇ ਅੱਗੇ ਵਧਦੇ 47ਵੀਂ ਸਿੱਖ ਦੇ ਸੂਰਬੀਰ",
    "image5.webp": "ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਪਰਸੀ ਗੇਰਾਲਡ ਵਾਕਰ, 47ਵੀਂ ਸਿੱਖ ਦੇ ਪਹਿਲੇ ਕਮਾਂਡਿੰਗ ਅਫਸਰ",
    "image3.webp": "47ਵੀਂ ਸਿੱਖ (ਇਤਿਹਾਸਕ ਤਸਵੀਰ)",
    "image4.webp": "47ਵੀਂ ਸਿੱਖ ਦਾ ਬੈਲਟ ਬਕਲ",
    "image1.webp": "ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਪਰਸੀ ਗੇਰਾਲਡ ਵਾਕਰ, 47ਵੀਂ ਸਿੱਖ ਦੇ ਪਹਿਲੇ ਕਮਾਂਡਿੰਗ ਅਫਸਰ",
    "image2.webp": "ਜਿੱਤ ਪਰੇਡ: ਪਹਿਲੇ ਵਿਸ਼ਵ ਯੁੱਧ ਤੋਂ ਬਾਅਦ ਲੰਡਨ ਦੇ ਪਾਲ ਮਾਲ ਵਿਖੇ ਮਾਰਚ ਕਰਦੇ 47ਵੀਂ ਸਿੱਖ ਦੇ ਜਵਾਨ ਤੇ ਅਫਸਰ",
    "image7.webp": "ਬਟਾਲੀਅਨ ਸਥਾਪਨਾ ਸਮੇਂ ਬ੍ਰਿਟਿਸ਼ ਅਤੇ ਭਾਰਤੀ ਅਫਸਰ",
    "image8.webp": "5 ਸਿੱਖ ਦੇ ਗਾਰਡ ਆਫ਼ ਆਨਰ ਦਾ ਨਿਰੀਖਣ ਕਰਦੇ ਜਨਰਲ ਮੁਹੰਮਦ ਮੂਸਾ"
}

CACHE = {}
if os.path.exists("translations_cache.json"):
    try:
        with open("translations_cache.json", "r", encoding="utf-8") as f:
            CACHE = json.load(f)
    except Exception:
        CACHE = {}

def save_cache():
    with open("translations_cache.json", "w", encoding="utf-8") as f:
        json.dump(CACHE, f, ensure_ascii=False, indent=2)

def trans_text(text, lang):
    t_str = str(text).strip()
    if not t_str or t_str.isdigit():
        return t_str
    if lang in CACHE and t_str in CACHE[lang]:
        return CACHE[lang][t_str]
    
    if len(t_str) > 350:
        words = t_str.split()
        chunks = []
        curr = []
        curr_len = 0
        for w in words:
            if curr_len + len(w) + 1 > 300:
                chunks.append(" ".join(curr))
                curr = [w]
                curr_len = len(w)
            else:
                curr.append(w)
                curr_len += len(w) + 1
        if curr:
            chunks.append(" ".join(curr))
            
        trans_chunks = []
        for c in chunks:
            c_clean = c.strip()
            if not c_clean: continue
            trans_chunks.append(trans_text(c_clean, lang))
        res = " ".join(trans_chunks)
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
            
    CACHE.setdefault(lang, {})[t_str] = t_str
    return t_str

def update_html_pages():
    print("Updating Successors HTML pages (EN, HI, PA)...")
    for item in SUCCESSORS_DATA:
        num = item["num"]
        en_file = f"art{num}.html"
        hi_file = f"art{num}_hi.html"
        pa_file = f"art{num}_pa.html"
        
        if not os.path.exists(en_file):
            print(f"Skipping {en_file}, file not found")
            continue
            
        with open(en_file, "r", encoding="utf-8") as f:
            soup_en = BeautifulSoup(f.read(), "html.parser")
            
        # Update English Page
        # Ensure Language Switcher Bar
        lang_bar = soup_en.find("div", class_="lang-switch-bar")
        if not lang_bar:
            lang_html = f"""<div class="lang-switch-bar" style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.85); padding: 8px 16px; border-radius: 14px; border: 1px solid var(--glass-border); margin-bottom: 20px; backdrop-filter: blur(12px);">
<a class="nav-link" href="index.html" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.4); color: #cbd5e1;">
    🏛️ Language Portal
</a>
<div style="display: flex; gap: 8px; align-items: center;">
<a class="nav-link" href="art{num}.html" style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24;">🇬🇧 English</a>
<a class="nav-link" href="art{num}_hi.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇮🇳 हिन्दी</a>
<a class="nav-link" href="art{num}_pa.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">ੴ ਪੰਜਾਬੀ</a>
</div>
</div>"""
            cont = soup_en.find("div", class_="gallery-container")
            if cont:
                cont.insert(0, BeautifulSoup(lang_html, "html.parser"))
                
        # Home button for EN
        home_btn_en = soup_en.find("a", href="index_en.html")
        if not home_btn_en:
            home_div = soup_en.find("div", style=re.compile(r"margin-bottom:\s*20px"))
            if home_div:
                home_div.clear()
                home_div.append(BeautifulSoup('<a class="nav-link" href="index_en.html" style="display: inline-flex; background: rgba(0,0,0,0.3); padding: 10px 20px; border-radius: 20px; border: 1px solid var(--glass-border);"><svg fill="none" height="20" stroke="currentColor" stroke-width="2" style="margin-right: 8px;" viewbox="0 0 24 24" width="20"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg> Back to Home</a>', 'html.parser'))
                
        # Ensure Audio section in EN
        aud_en = soup_en.find("audio")
        if aud_en: aud_en["src"] = f"assets/audio/audio_{num}.mp3"
        
        with open(en_file, "w", encoding="utf-8") as f:
            f.write(str(soup_en))
            
        # ==================== BUILD HINDI PAGE ====================
        soup_hi = BeautifulSoup(str(soup_en), "html.parser")
        if soup_hi.title: soup_hi.title.string = f"{item['title_hi']} - विरासत संग्रहालय"
        
        # Switcher Bar
        bar_hi = soup_hi.find("div", class_="lang-switch-bar")
        if bar_hi:
            bar_hi.clear()
            bar_hi_html = f"""<a class="nav-link" href="index_hi.html" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.4); color: #cbd5e1;">
    🏛️ भाषा चयन
</a>
<div style="display: flex; gap: 8px; align-items: center;">
<a class="nav-link" href="art{num}.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇬🇧 English</a>
<a class="nav-link" href="art{num}_hi.html" style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24;">🇮🇳 हिन्दी</a>
<a class="nav-link" href="art{num}_pa.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">ੴ ਪੰਜਾਬੀ</a>
</div>"""
            bar_hi.append(BeautifulSoup(bar_hi_html, "html.parser"))
            
        # Home button for HI
        home_link_hi = soup_hi.find("a", href=re.compile(r"index.*\.html"))
        if home_link_hi:
            home_link_hi["href"] = "index_hi.html"
            home_link_hi.clear()
            home_link_hi.append(BeautifulSoup('<svg fill="none" height="20" stroke="currentColor" stroke-width="2" style="margin-right: 8px;" viewbox="0 0 24 24" width="20"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg> मुख्य पृष्ठ पर वापस', 'html.parser'))
            
        h1_hi = soup_hi.find("h1")
        if h1_hi: h1_hi.string = item["title_hi"]
        
        # Translate Scroller for 605 and 607 if present
        track_hi = soup_hi.find("div", class_="scroller-track")
        if track_hi:
            for item_div in track_hi.find_all("div", class_="scroller-item"):
                img = item_div.find("img")
                nom = item_div.find("div", class_="nomenclature")
                if img and nom:
                    src = img.get("src", "")
                    if num == 605:
                        for k, v in CAPTIONS_605_HI.items():
                            if k in src:
                                nom.string = v
                                img["alt"] = v
                                break
                    elif num == 607:
                        for k, v in CAPTIONS_607_HI.items():
                            if k in src:
                                nom.string = v
                                img["alt"] = v
                                break
                                
        # Audio Section
        aud_hi = soup_hi.find("audio")
        if aud_hi: aud_hi["src"] = f"assets/audio_hi/audio_{num}.mp3"
        play_btn_hi = soup_hi.find("button", class_="play-btn")
        if play_btn_hi:
            play_btn_hi.clear()
            play_btn_hi.append(BeautifulSoup('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg> वर्णन सुनें', 'html.parser'))
            
        # Description Boxes
        boxes_hi = soup_hi.find_all("div", class_="description-box")
        if len(boxes_hi) > 0:
            meta_html = f"""<strong>शीर्षक:</strong> {item['title_hi']}<br/>
<strong>श्रेणी:</strong> {item['category_hi']}<br/>
<strong>रेजिमेंट:</strong> सिख रेजिमेंट<br/>"""
            boxes_hi[0].clear()
            boxes_hi[0].append(BeautifulSoup(meta_html, "html.parser"))
            
        if len(boxes_hi) > 1:
            body_box_en = soup_en.find_all("div", class_="description-box")[1]
            paras_hi = []
            for p_tag in body_box_en.find_all("p"):
                p_txt = p_tag.get_text().strip()
                if p_txt:
                    trans_p = trans_text(p_txt, "hi")
                    # Clean acronyms
                    trans_p = re.sub(r'\bXIV\b', '14वीं', trans_p)
                    trans_p = re.sub(r'\bXV\b', '15वीं', trans_p)
                    trans_p = re.sub(r'\bXLV\b', '45वीं', trans_p)
                    trans_p = re.sub(r'\bXXXV\b', '35वीं', trans_p)
                    trans_p = re.sub(r'\bXXXVI\b', '36वीं', trans_p)
                    trans_p = re.sub(r'\bXLVII\b', '47वीं', trans_p)
                    trans_p = re.sub(r'\bSIKH\b', 'सिख', trans_p, flags=re.I)
                    trans_p = re.sub(r'\bSIKHS\b', 'सिख', trans_p, flags=re.I)
                    trans_p = re.sub(r'\bRATTRAYS\b', 'रैट्रेज़', trans_p, flags=re.I)
                    trans_p = re.sub(r'\bRATTRAY\b', 'रैट्रे', trans_p, flags=re.I)
                    paras_hi.append(trans_p)
            boxes_hi[1].clear()
            for p_t in paras_hi:
                p_el = soup_hi.new_tag("p")
                p_el.string = p_t
                boxes_hi[1].append(p_el)
                
        # Localized Navigation
        prev_btn_hi = soup_hi.find("a", string=re.compile(r"Previous|पिछली"))
        if prev_btn_hi:
            prev_btn_hi.string = "पिछली कलाकृति"
        next_btn_hi = soup_hi.find("a", string=re.compile(r"Next|अगली"))
        if next_btn_hi:
            next_btn_hi.string = "अगली कलाकृति"
            
        # QR Code Section
        qr_h3 = soup_hi.find("div", class_="qr-info")
        if qr_h3:
            h3 = qr_h3.find("h3")
            if h3: h3.string = "मोबाइल पर खोलें"
            p = qr_h3.find("p")
            if p: p.string = "अपने फोन पर इस कलाकृति को देखने के लिए स्कैन करें।"
            
        with open(hi_file, "w", encoding="utf-8") as f:
            f.write(str(soup_hi))
            
        # ==================== BUILD PUNJABI PAGE ====================
        soup_pa = BeautifulSoup(str(soup_en), "html.parser")
        if soup_pa.title: soup_pa.title.string = f"{item['title_pa']} - ਵਿਰਾਸਤ ਅਜਾਇਬ ਘਰ"
        
        # Switcher Bar
        bar_pa = soup_pa.find("div", class_="lang-switch-bar")
        if bar_pa:
            bar_pa.clear()
            bar_pa_html = f"""<a class="nav-link" href="index_pa.html" style="padding: 6px 14px; font-size: 0.85rem; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.4); color: #cbd5e1;">
    🏛️ ਭਾਸ਼ਾ ਚੋਣ
</a>
<div style="display: flex; gap: 8px; align-items: center;">
<a class="nav-link" href="art{num}.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇬🇧 English</a>
<a class="nav-link" href="art{num}_hi.html" style="padding: 6px 12px; font-size: 0.85rem; border-radius: 20px;">🇮🇳 हिन्दी</a>
<a class="nav-link" href="art{num}_pa.html" style="background: rgba(245, 158, 11, 0.35); border-color: #f59e0b; font-weight: 700; color: #fbbf24;">ੴ ਪੰਜਾਬੀ</a>
</div>"""
            bar_pa.append(BeautifulSoup(bar_pa_html, "html.parser"))
            
        # Home button for PA
        home_link_pa = soup_pa.find("a", href=re.compile(r"index.*\.html"))
        if home_link_pa:
            home_link_pa["href"] = "index_pa.html"
            home_link_pa.clear()
            home_link_pa.append(BeautifulSoup('<svg fill="none" height="20" stroke="currentColor" stroke-width="2" style="margin-right: 8px;" viewbox="0 0 24 24" width="20"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg> ਮੁੱਖ ਪੰਨੇ \'ਤੇ ਵਾਪਸ', 'html.parser'))
            
        h1_pa = soup_pa.find("h1")
        if h1_pa: h1_pa.string = item["title_pa"]
        
        # Translate Scroller for 605 and 607 if present
        track_pa = soup_pa.find("div", class_="scroller-track")
        if track_pa:
            for item_div in track_pa.find_all("div", class_="scroller-item"):
                img = item_div.find("img")
                nom = item_div.find("div", class_="nomenclature")
                if img and nom:
                    src = img.get("src", "")
                    if num == 605:
                        for k, v in CAPTIONS_605_PA.items():
                            if k in src:
                                nom.string = v
                                img["alt"] = v
                                break
                    elif num == 607:
                        for k, v in CAPTIONS_607_PA.items():
                            if k in src:
                                nom.string = v
                                img["alt"] = v
                                break
                                
        # Audio Section
        aud_pa = soup_pa.find("audio")
        if aud_pa: aud_pa["src"] = f"assets/audio_pa/audio_{num}.mp3"
        play_btn_pa = soup_pa.find("button", class_="play-btn")
        if play_btn_pa:
            play_btn_pa.clear()
            play_btn_pa.append(BeautifulSoup('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg> ਵੇਰਵਾ ਸੁਣੋ', 'html.parser'))
            
        # Description Boxes
        boxes_pa = soup_pa.find_all("div", class_="description-box")
        if len(boxes_pa) > 0:
            meta_html = f"""<strong>ਸਿਰਲੇਖ:</strong> {item['title_pa']}<br/>
<strong>ਸ਼੍ਰੇਣੀ:</strong> {item['category_pa']}<br/>
<strong>ਰੈਜੀਮੈਂਟ:</strong> ਸਿੱਖ ਰੈਜੀਮੈਂਟ<br/>"""
            boxes_pa[0].clear()
            boxes_pa[0].append(BeautifulSoup(meta_html, "html.parser"))
            
        if len(boxes_pa) > 1:
            body_box_en = soup_en.find_all("div", class_="description-box")[1]
            paras_pa = []
            for p_tag in body_box_en.find_all("p"):
                p_txt = p_tag.get_text().strip()
                if p_txt:
                    trans_p = trans_text(p_txt, "pa")
                    # Clean acronyms
                    trans_p = re.sub(r'\bXIV\b', '14ਵੀਂ', trans_p)
                    trans_p = re.sub(r'\bXV\b', '15ਵੀਂ', trans_p)
                    trans_p = re.sub(r'\bXLV\b', '45ਵੀਂ', trans_p)
                    trans_p = re.sub(r'\bXXXV\b', '35ਵੀਂ', trans_p)
                    trans_p = re.sub(r'\bXXXVI\b', '36ਵੀਂ', trans_p)
                    trans_p = re.sub(r'\bXLVII\b', '47ਵੀਂ', trans_p)
                    trans_p = re.sub(r'\bSIKH\b', 'ਸਿੱਖ', trans_p, flags=re.I)
                    trans_p = re.sub(r'\bSIKHS\b', 'ਸਿੱਖ', trans_p, flags=re.I)
                    trans_p = re.sub(r'\bRATTRAYS\b', 'ਰੈਟਰੇਜ਼', trans_p, flags=re.I)
                    trans_p = re.sub(r'\bRATTRAY\b', 'ਰੈਟਰੇ', trans_p, flags=re.I)
                    paras_pa.append(trans_p)
            boxes_pa[1].clear()
            for p_t in paras_pa:
                p_el = soup_pa.new_tag("p")
                p_el.string = p_t
                boxes_pa[1].append(p_el)
                
        # Localized Navigation
        prev_btn_pa = soup_pa.find("a", string=re.compile(r"Previous|ਪਿਛਲੀ"))
        if prev_btn_pa:
            prev_btn_pa.string = "ਪਿਛਲੀ ਕਲਾਕ੍ਰਿਤੀ"
        next_btn_pa = soup_pa.find("a", string=re.compile(r"Next|ਅਗਲੀ"))
        if next_btn_pa:
            next_btn_pa.string = "ਅਗਲੀ ਕਲਾਕ੍ਰਿਤੀ"
            
        # QR Code Section
        qr_h3 = soup_pa.find("div", class_="qr-info")
        if qr_h3:
            h3 = qr_h3.find("h3")
            if h3: h3.string = "ਮੋਬਾਈਲ 'ਤੇ ਖੋਲ੍ਹੋ"
            p = qr_h3.find("p")
            if p: p.string = "ਆਪਣੇ ਫ਼ੋਨ 'ਤੇ ਇਸ ਕਲਾ ਰਿਕਾਰਡ ਨੂੰ ਦੇਖਣ ਲਈ ਸਕੈਨ ਕਰੋ।"
            
        with open(pa_file, "w", encoding="utf-8") as f:
            f.write(str(soup_pa))

    save_cache()
    print("All Successors HTML pages generated successfully!")

def update_dropdowns():
    print("Updating dropdown-8 in index_en.html, index_hi.html, index_pa.html...")
    
    # 1. English Dropdown
    with open("index_en.html", "r", encoding="utf-8") as f:
        soup_en = BeautifulSoup(f.read(), "html.parser")
    dd_en = soup_en.find("div", id="dropdown-8")
    if dd_en:
        dd_en_html = """<a href="art601.html">XIV Firozpure Sikhs</a>
<a href="art602.html">XV Ludhiana Sikhs</a>
<a href="art603.html">XLV Rattray's Sikhs</a>
<a href="art604.html">XXXV Sikhs</a>
<a href="art605.html">Re-organisation of the Indian Army (1922)</a>
<a href="art606.html">XXXVI Sikhs</a>
<a href="art607.html">XLVII Sikhs</a>"""
        dd_en.clear()
        dd_en.append(BeautifulSoup(dd_en_html, "html.parser"))
        with open("index_en.html", "w", encoding="utf-8") as f:
            f.write(str(soup_en))

    # 2. Hindi Dropdown
    with open("index_hi.html", "r", encoding="utf-8") as f:
        soup_hi = BeautifulSoup(f.read(), "html.parser")
    dd_hi = soup_hi.find("div", id="dropdown-8")
    if dd_hi:
        dd_hi_html = """<a href="art601_hi.html">14वीं फिरोजपुर सिख</a>
<a href="art602_hi.html">15वीं लुधियाना सिख</a>
<a href="art603_hi.html">45वीं रैट्रेज़ सिख</a>
<a href="art604_hi.html">35वीं सिख</a>
<a href="art605_hi.html">भारतीय सेना का पुनर्गठन (1922)</a>
<a href="art606_hi.html">36वीं सिख</a>
<a href="art607_hi.html">47वीं सिख</a>"""
        dd_hi.clear()
        dd_hi.append(BeautifulSoup(dd_hi_html, "html.parser"))
        with open("index_hi.html", "w", encoding="utf-8") as f:
            f.write(str(soup_hi))

    # 3. Punjabi Dropdown
    with open("index_pa.html", "r", encoding="utf-8") as f:
        soup_pa = BeautifulSoup(f.read(), "html.parser")
    dd_pa = soup_pa.find("div", id="dropdown-8")
    if dd_pa:
        dd_pa_html = """<a href="art601_pa.html">14ਵੀਂ ਫਿਰੋਜ਼ਪੁਰ ਸਿੱਖ</a>
<a href="art602_pa.html">15ਵੀਂ ਲੁਧਿਆਣਾ ਸਿੱਖ</a>
<a href="art603_pa.html">45ਵੀਂ ਰੈਟਰੇਜ਼ ਸਿੱਖ</a>
<a href="art604_pa.html">35ਵੀਂ ਸਿੱਖ</a>
<a href="art605_pa.html">ਭਾਰਤੀ ਫੌਜ ਦਾ ਪੁਨਰਗਠਨ (1922)</a>
<a href="art606_pa.html">36ਵੀਂ ਸਿੱਖ</a>
<a href="art607_pa.html">47ਵੀਂ ਸਿੱਖ</a>"""
        dd_pa.clear()
        dd_pa.append(BeautifulSoup(dd_pa_html, "html.parser"))
        with open("index_pa.html", "w", encoding="utf-8") as f:
            f.write(str(soup_pa))

    print("Dropdown-8 navigation synchronized across all three language portals.")

async def generate_smart_audios():
    print("Synthesizing ~100-word smart audio recitations in English, Hindi, and Punjabi...")
    os.makedirs("assets/audio", exist_ok=True)
    os.makedirs("assets/audio_hi", exist_ok=True)
    os.makedirs("assets/audio_pa", exist_ok=True)
    
    for item in SUCCESSORS_DATA:
        num = item["num"]
        
        # 1. English Audio
        en_path = f"assets/audio/audio_{num}.mp3"
        try:
            communicate = edge_tts.Communicate(item["summary_en"], "en-IN-PrabhatNeural")
            await communicate.save(en_path)
            print(f"EN audio generated for art{num}")
        except Exception as e:
            print(f"Fallback gTTS for EN art{num}: {e}")
            tts = gTTS(text=item["summary_en"], lang='en')
            tts.save(en_path)
            
        # 2. Hindi Audio
        hi_path = f"assets/audio_hi/audio_{num}.mp3"
        try:
            communicate = edge_tts.Communicate(item["summary_hi"], "hi-IN-MadhurNeural")
            await communicate.save(hi_path)
            print(f"HI audio generated for art{num}")
        except Exception as e:
            print(f"Fallback gTTS for HI art{num}: {e}")
            tts = gTTS(text=item["summary_hi"], lang='hi')
            tts.save(hi_path)
            
        # 3. Punjabi Audio
        pa_path = f"assets/audio_pa/audio_{num}.mp3"
        try:
            tts = gTTS(text=item["summary_pa"], lang='pa')
            tts.save(pa_path)
            print(f"PA audio generated for art{num}")
        except Exception as e:
            print(f"Error PA audio for art{num}: {e}")

def main():
    print("=== STARTING SUCCESSORS OVERHAUL ===")
    update_html_pages()
    update_dropdowns()
    asyncio.run(generate_smart_audios())
    print("=== SUCCESSORS OVERHAUL COMPLETED SUCCESSFULLY! ===")

if __name__ == "__main__":
    main()
