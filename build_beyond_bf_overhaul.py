import os, sys, re, json, asyncio
from bs4 import BeautifulSoup
import edge_tts
from gtts import gTTS
from deep_translator import GoogleTranslator

# Exhibits in Beyond Battle Fd
EXHIBITS_DATA = [
    {
        "num": 507,
        "title_en": "HH Maharaja Yadavindra Singh",
        "title_hi": "महाराजा यादविंद्र सिंह",
        "title_pa": "ਮਹਾਰਾਜਾ ਯਾਦਵਿੰਦਰ ਸਿੰਘ",
        "category_en": "Regimental Icons",
        "category_hi": "रेजिमेंटल प्रतीक",
        "category_pa": "ਰੈਜੀਮੈਂਟਲ ਆਈਕਨ",
        "summary_en": "Maharaja Yadavindra Singh (1913–1974), the ninth and last ruling Maharaja of Patiala, was an iconic leader and honorary Colonel of the Sikh Regiment. Commissioned into the Regiment in 1935, he served with 2 Sikh in Malaya and during World War II in the Middle East and Italy. A legendary cricketer who played Test cricket for India and served as President of the Indian Olympic Association, he played a crucial patriotic role in 1947 by being among the first rulers to integrate his princely state into the Indian Union. He served as Rajpramukh of PEPSU and India's Ambassador to Italy and the Netherlands.",
        "summary_hi": "महाराजा यादविंद्र सिंह (1913–1974), पटियाला के अंतिम शासक और सिख रेजिमेंट के प्रतिष्ठित कर्नल थे। 1935 में रेजिमेंट में कमीशन प्राप्त कर उन्होंने मलाया, मध्य पूर्व और इटली में दूसरे विश्व युद्ध के दौरान विशिष्ट सेवाएं दीं। वे एक कुशल टेस्ट क्रिकेटर और भारतीय ओलंपिक संघ के अध्यक्ष भी रहे। 1947 में स्वतंत्रता के समय उन्होंने अपनी रियासत का भारत संघ में सर्वप्रथम विलय कर ऐतिहासिक देशभक्ति का परिचय दिया। वे पेप्सू के राजप्रमुख तथा इटली व नीदरलैंड में भारत के राजदूत रहे।",
        "summary_pa": "ਮਹਾਰਾਜਾ ਯਾਦਵਿੰਦਰ ਸਿੰਘ (1913–1974), ਪਟਿਆਲਾ ਰਿਆਸਤ ਦੇ ਆਖਰੀ ਸ਼ਾਸਕ ਅਤੇ ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦੇ ਪ੍ਰਮੁੱਖ ਆਈਕਨ ਸਨ। 1935 ਵਿੱਚ ਰੈਜੀਮੈਂਟ ਵਿੱਚ ਕਮਿਸ਼ਨ ਲੈ ਕੇ ਉਨ੍ਹਾਂ ਨੇ ਦੂਜੇ ਵਿਸ਼ਵ ਯੁੱਧ ਦੌਰਾਨ ਮਲਾਇਆ, ਮੱਧ ਪੂਰਬ ਅਤੇ ਇਟਲੀ ਵਿੱਚ ਸੇਵਾ ਨਿਭਾਈ। ਇੱਕ ਉੱਘੇ ਟੈਸਟ ਕ੍ਰਿਕਟਰ ਅਤੇ ਭਾਰਤੀ ਓਲੰਪਿਕ ਐਸੋਸੀਏਸ਼ਨ ਦੇ ਪ੍ਰਧਾਨ ਵਜੋਂ ਉਨ੍ਹਾਂ ਖੇਡਾਂ ਨੂੰ ਉਤਸ਼ਾਹਿਤ ਕੀਤਾ। 1947 ਵਿੱਚ ਉਨ੍ਹਾਂ ਨੇ ਆਪਣੀ ਰਿਆਸਤ ਦਾ ਭਾਰਤੀ ਸੰਘ ਵਿੱਚ ਰਲੇਵਾਂ ਕਰਕੇ ਮਿਸਾਲੀ ਦੇਸ਼ਭਗਤੀ ਦਿਖਾਈ। ਉਹ ਪੈਪਸੂ ਦੇ ਰਾਜਪ੍ਰਮੁੱਖ ਅਤੇ ਇਟਲੀ ਤੇ ਨੀਦਰਲੈਂਡ ਵਿੱਚ ਭਾਰਤ ਦੇ ਰਾਜਦੂਤ ਰਹੇ।"
    },
    {
        "num": 508,
        "title_en": "Lt Gen Harbakhsh Singh, VrC",
        "title_hi": "लेफ्टिनेंट जनरल हरबख्श सिंह, वीआरसी",
        "title_pa": "ਲੈਫਟੀਨੈਂਟ ਜਨਰਲ ਹਰਬਖ਼ਸ਼ ਸਿੰਘ, ਵੀਆਰਸੀ",
        "category_en": "Regimental Icons",
        "category_hi": "रेजिमेंटल प्रतीक",
        "category_pa": "ਰੈਜੀਮੈਂਟਲ ਆਈਕਨ",
        "summary_en": "Lieutenant General Harbakhsh Singh, Padma Vibhushan, Padma Bhushan, Vir Chakra, is a legendary commander of the Sikh Regiment and the Indian Army. Commissioned into 5/11 Sikh in 1935, he survived brutal imprisonment as a POW in Malaya during World War II. In 1947, he commanded 1 Sikh and personally led the recapture of Shelatang and Uri, earning the Vir Chakra. As Western Army Commander during the 1965 Indo-Pak War, his resolute leadership, tactical genius, and defiance of withdrawal orders led to decisive Indian victories at Asal Uttar and the Lahore and Sialkot sectors, thwarting the Pakistani offensive.",
        "summary_hi": "लेफ्टिनेंट जनरल हरबख्श सिंह (पद्म विभूषण, पद्म भूषण, वीर चक्र) भारतीय सेना और सिख रेजिमेंट के एक महान सेनानायक थे। 1935 में 5/11 सिख में कमीशन पाकर उन्होंने द्वितीय विश्व युद्ध में अदम्य साहस दिखाया और मलाया में युद्धबंदी रहे। 1947 में 1 सिख की कमान संभालते हुए उन्होंने शेलातेंग और उरी को मुक्त कराया और वीर चक्र प्राप्त किया। 1965 के भारत-पाक युद्ध में पश्चिमी कमान के कमांडर के रूप में उनके दृढ़ नेतृत्व और रणनीतिक कौशल ने असल उत्तर और लाहौर सेक्टर में भारतीय सेना को ऐतिहासिक विजय दिलाई।",
        "summary_pa": "ਲੈਫਟੀਨੈਂਟ ਜਨਰਲ ਹਰਬਖ਼ਸ਼ ਸਿੰਘ (ਪਦਮ ਵਿਭੂਸ਼ਨ, ਪਦਮ ਭੂਸ਼ਨ, ਵੀਰ ਚੱਕਰ) ਭਾਰਤੀ ਫੌਜ ਅਤੇ ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦੇ ਇੱਕ ਮਹਾਨ ਜਰਨੈਲ ਸਨ। 1935 ਵਿੱਚ 5/11 ਸਿੱਖ ਵਿੱਚ ਸ਼ਾਮਲ ਹੋ ਕੇ ਉਨ੍ਹਾਂ ਨੇ ਦੂਜੇ ਵਿਸ਼ਵ ਯੁੱਧ ਦੌਰਾਨ ਬਹਾਦਰੀ ਦਿਖਾਈ। 1947 ਵਿੱਚ 1 ਸਿੱਖ ਦੀ ਕਮਾਨ ਸੰਭਾਲਦਿਆਂ ਉਨ੍ਹਾਂ ਸ਼ਲਾਟੇਂਗ ਅਤੇ ਉੜੀ ਨੂੰ ਆਜ਼ਾਦ ਕਰਵਾਇਆ ਅਤੇ ਵੀਰ ਚੱਕਰ ਪ੍ਰਾਪਤ ਕੀਤਾ। 1965 ਦੀ ਭਾਰਤ-ਪਾਕਿ ਜੰਗ ਦੌਰਾਨ ਪੱਛਮੀ ਕਮਾਂਡ ਦੇ ਮੁਖੀ ਵਜੋਂ ਉਨ੍ਹਾਂ ਦੀ ਦਲੇਰਾਨਾ ਅਗਵਾਈ ਨੇ ਅਸਲ ਉੱਤਰ ਅਤੇ ਲਾਹੌਰ ਸੈਕਟਰ ਵਿੱਚ ਦੁਸ਼ਮਣ ਨੂੰ ਕਰਾਰੀ ਹਾਰ ਦੇ ਕੇ ਇਤਿਹਾਸਕ ਜਿੱਤ ਦਰਜ ਕੀਤੀ।"
    },
    {
        "num": 509,
        "title_en": "General RA Savory, KCIE, CB, DSO, MC",
        "title_hi": "जनरल आर.ए. सेवरी, केसीआईई, सीबी, डीएसओ, एमसी",
        "title_pa": "ਜਨਰਲ ਆਰ.ਏ. ਸੇਵਰੀ, ਕੇਸੀਆਈਈ, ਸੀਬੀ, ਡੀਐਸਓ, ਐਮਸੀ",
        "category_en": "Regimental Icons",
        "category_hi": "रेजिमेंटल प्रतीक",
        "category_pa": "ਰੈਜੀਮੈਂਟਲ ਆਈਕਨ",
        "summary_en": "Lieutenant General Sir Reginald Arthur Savory (1894–1980) was a distinguished military commander with a lifelong affection for the Sikh Regiment. Commissioned in 1914 into the 14th Ferozepore Sikhs, he fought gallantly in Gallipoli (1915), Mesopotamia, and Persia, earning the Military Cross. During World War II, he commanded the 11th Indian Infantry Brigade at Keren and the 23rd Indian Division in the Burma Campaign, later rising to Adjutant General of the Indian Army. Known as the 'Father of the Modern Sikh Regiment', he maintained deep, affectionate bonds with the Sikh troops throughout his life.",
        "summary_hi": "लेफ्टिनेंट जनरल सर रेजिनाल्ड आर्थर सेवरी (1894–1980) सिख रेजिमेंट से गहरा जुड़ाव रखने वाले एक प्रसिद्ध सैन्य कमांडर थे। 1914 में 14वीं फिरोजपुर सिख में कमीशन प्राप्त कर उन्होंने गैलीपोली (1915), मेसोपोटामिया और फारस में अदम्य वीरता दिखाई और मिलिट्री क्रॉस अर्जित किया। द्वितीय विश्व युद्ध के दौरान उन्होंने केरेन में 11वीं इन्फैंट्री ब्रिगेड और बर्मा में 23वीं डिवीजन की कमान संभाली तथा बाद में भारतीय सेना के एडजुटेंट जनरल बने। 'आधुनिक सिख रेजिमेंट के जनक' के रूप में विख्यात जनरल सेवरी ने जीवनपर्यंत सिख सैनिकों के साथ अटूट स्नेह बनाए रखा।",
        "summary_pa": "ਲੈਫਟੀਨੈਂਟ ਜਨਰਲ ਸਰ ਰੇਜੀਨਾਲਡ ਆਰਥਰ ਸੇਵਰੀ (1894–1980) ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਨਾਲ ਗੂੜ੍ਹਾ ਪਿਆਰ ਰੱਖਣ ਵਾਲੇ ਇੱਕ ਉੱਘੇ ਕਮਾਂਡਰ ਸਨ। 1914 ਵਿੱਚ 14ਵੀਂ ਫਿਰੋਜ਼ਪੁਰ ਸਿੱਖ ਵਿੱਚ ਕਮਿਸ਼ਨ ਹਾਸਲ ਕਰਕੇ ਉਨ੍ਹਾਂ ਗੈਲੀਪੋਲੀ (1915), ਮੇਸੋਪੋਟੇਮੀਆ ਅਤੇ ਫ਼ਾਰਸ ਵਿੱਚ ਬਹਾਦਰੀ ਨਾਲ ਲੜਦਿਆਂ ਮਿਲਟਰੀ ਕਰਾਸ ਜਿੱਤਿਆ। ਦੂਜੇ ਵਿਸ਼ਵ ਯੁੱਧ ਵਿੱਚ ਉਨ੍ਹਾਂ ਕੇਰੇਨ ਵਿਖੇ 11ਵੀਂ ਬ੍ਰਿਗੇਡ ਅਤੇ ਬਰਮਾ ਵਿੱਚ 23ਵੀਂ ਡਿਵੀਜ਼ਨ ਦੀ ਅਗਵਾਈ ਕੀਤੀ ਅਤੇ ਬਾਅਦ ਵਿੱਚ ਭਾਰਤੀ ਫੌਜ ਦੇ ਐਡਜੂਟੈਂਟ ਜਨਰਲ ਬਣੇ। 'ਆਧੁਨਿਕ ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦੇ ਪਿਤਾਮਾ' ਵਜੋਂ ਜਾਣੇ ਜਾਂਦੇ ਸੇਵਰੀ ਨੇ ਸਾਰੀ ਉਮਰ ਸਿੱਖ ਜਵਾਨਾਂ ਨਾਲ ਅਟੁੱਟ ਨਾਤਾ ਬਣਾਈ ਰੱਖਿਆ।"
    },
    {
        "num": 501,
        "title_en": "History of Sikh Regimental Band",
        "title_hi": "सिख रेजिमेंटल बैंड का इतिहास",
        "title_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਬੈਂਡ ਦਾ ਇਤਿਹਾਸ",
        "category_en": "Beyond Battle Fd",
        "category_hi": "जंगी मैदान से परे",
        "category_pa": "ਜੰਗੀ ਮੈਦਾਨ ਤੋਂ ਪਰੇ",
        "summary_en": "The musical heritage of the Sikh Regiment traces back to Maharaja Ranjit Singh's era and the regiment's earliest raisings in 1846. The Pipe and Brass bands were formally raised in the 19th century, blending traditional Scottish bagpipes with Indian martial rhythms. The Sikh Regimental Band has performed globally with distinction, winning numerous premier military band competitions, playing at royal coronation ceremonies, Rashtrapati Bhavan state banquets, and Republic Day parades. Renowned for its impeccable drill, vibrant turbans, and soul-stirring martial tunes like 'Deh Shiva Bar Mohe Ehe', it remains a symbol of regimental pride and discipline.",
        "summary_hi": "सिख रेजिमेंट के बैंड की समृद्ध परंपरा महाराजा रणजीत सिंह के काल और 1846 में रेजिमेंट की स्थापना से जुड़ी है। 19वीं सदी में स्थापित पाइप और ब्रास बैंड ने पारंपरिक स्कॉटिश पाइप्स को भारतीय सैन्य धुनों के साथ खूबसूरती से जोड़ा। सिख रेजिमेंटल बैंड ने देश-विदेश में अपनी उत्कृष्ट प्रस्तुतियों से अनेक राष्ट्रीय एवं अंतरराष्ट्रीय प्रतियोगिताएं जीती हैं। राष्ट्रपति भवन के राजकीय समारोहों और गणतंत्र दिवस परेड में अपनी सधी हुई ड्रिल, भव्य पगड़ियों और 'देह शिवा बर मोहे इहै' जैसी ओजस्वी धुनों के साथ यह बैंड रेजिमेंट के गौरव का जीवंत प्रतीक है।",
        "summary_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦੇ ਬੈਂਡ ਦਾ ਇਤਿਹਾਸ ਮਹਾਰਾਜਾ ਰਣਜੀਤ ਸਿੰਘ ਦੇ ਦੌਰ ਅਤੇ 1846 ਵਿੱਚ ਰੈਜੀਮੈਂਟ ਦੀ ਸਥਾਪਨਾ ਨਾਲ ਜੁੜਿਆ ਹੈ। 19ਵੀਂ ਸਦੀ ਵਿੱਚ ਬਣੇ ਪਾਈਪ ਅਤੇ ਬ੍ਰਾਸ ਬੈਂਡ ਨੇ ਰਵਾਇਤੀ ਸਕਾਟਿਸ਼ ਬੈਗਪਾਈਪਾਂ ਨੂੰ ਖਾਲਸਾਈ ਜੰਗੀ ਧੁਨਾਂ ਨਾਲ ਬਾਖ਼ੂਬੀ ਮਿਲਾਇਆ। ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਬੈਂਡ ਨੇ ਦੇਸ਼-ਵਿਦੇਸ਼ ਵਿੱਚ ਸ਼ਾਨਦਾਰ ਪ੍ਰਦਰਸ਼ਨ ਕਰਕੇ ਅਨੇਕਾਂ ਫੌਜੀ ਮੁਕਾਬਲੇ ਜਿੱਤੇ ਹਨ। ਗਣਤੰਤਰ ਦਿਵਸ ਪਰੇਡਾਂ ਅਤੇ ਰਾਸ਼ਟਰਪਤੀ ਭਵਨ ਦੇ ਸਮਾਗਮਾਂ ਵਿੱਚ ਆਪਣੀ ਬਿਹਤਰੀਨ ਡ੍ਰਿਲ, ਸ਼ਾਨਦਾਰ ਦਸਤਾਰਾਂ ਅਤੇ 'ਦੇਹ ਸ਼ਿਵਾ ਬਰ ਮੋਹਿ ਇਹੈ' ਵਰਗੀਆਂ ਜੋਸ਼ੀਲੀਆਂ ਧੁਨਾਂ ਰਾਹੀਂ ਇਹ ਰੈਜੀਮੈਂਟ ਦੀ ਸ਼ਾਨ ਵਧਾ ਰਿਹਾ ਹੈ।"
    },
    {
        "num": 502,
        "title_en": "Sporting Prowess of the Sikhs",
        "title_hi": "सिखों की खेल उत्कृष्टता",
        "title_pa": "ਸਿੱਖਾਂ ਦੀ ਖੇਡ ਪ੍ਰਤਿਭਾ",
        "category_en": "Beyond Battle Fd",
        "category_hi": "जंगी मैदान से परे",
        "category_pa": "ਜੰਗੀ ਮੈਦਾਨ ਤੋਂ ਪਰੇ",
        "summary_en": "Beyond the battlefield, the Sikh Regiment boasts a storied legacy of excellence in national and international sports. Nurturing athletic talent with rigorous physical culture and regimental pride, the regiment has produced legendary Olympians, Asian Games champions, and National record holders across athletics, hockey, wrestling, shooting, rowing, and boxing. Icons like Olympian Milkha Singh (The Flying Sikh), Harichand, and numerous international medalists have donned the regimental colors, exemplifying unmatched stamina, sportsmanship, and grit. The Sikh Regimental Centre remains a premier sports nursery in India, fostering champions who uphold the motto of courage and victory.",
        "summary_hi": "युद्धभूमि के साथ-साथ सिख रेजिमेंट का राष्ट्रीय और अंतरराष्ट्रीय खेलों में भी गौरवशाली इतिहास रहा है। रेजिमेंट ने अपने उत्कृष्ट खेल संवर्धन से अनेक महान ओलंपियन, एशियाई खेल पदक विजेता और राष्ट्रीय चैंपियन तैयार किए हैं। 'फ्लाइंग सिख' मिल्खा सिंह, ओलंपियन हरिचंद और अनेक अंतरराष्ट्रीय पदक विजेताओं ने रेजिमेंट की जर्सी पहनकर एथलेटिक्स, हॉकी, कुश्ती, नौकायन और मुक्केबाजी में देश का नाम रोशन किया। सिख रेजिमेंटल सेंटर भारतीय सेना की एक प्रमुख खेल नर्सरी है, जो जवानों में अदम्य सहनशक्ति, अनुशासन और खेल भावना का संचार करती है।",
        "summary_pa": "ਜੰਗ ਦੇ ਮੈਦਾਨ ਤੋਂ ਇਲਾਵਾ ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦਾ ਖੇਡਾਂ ਦੇ ਖੇਤਰ ਵਿੱਚ ਵੀ ਇੱਕ ਸ਼ਾਨਦਾਰ ਇਤਿਹਾਸ ਹੈ। ਰੈਜੀਮੈਂਟ ਨੇ ਸ਼ਾਨਦਾਰ ਸਿਖਲਾਈ ਰਾਹੀਂ ਕਈ ਉਲੰਪੀਅਨ, ਏਸ਼ੀਆਈ ਖੇਡਾਂ ਦੇ ਚੈਂਪੀਅਨ ਅਤੇ ਰਾਸ਼ਟਰੀ ਰਿਕਾਰਡ ਧਾਰਕ ਪੈਦਾ ਕੀਤੇ ਹਨ। 'ਫਲਾਇੰਗ ਸਿੱਖ' ਮਿਲਖਾ ਸਿੰਘ, ਹਰੀ ਚੰਦ ਅਤੇ ਕਈ ਅੰਤਰਰਾਸ਼ਟਰੀ ਤਗਮਾ ਜੇਤੂਆਂ ਨੇ ਐਥਲੈਟਿਕਸ, ਹਾਕੀ, ਕੁਸ਼ਤੀ ਅਤੇ ਮੁੱਕੇਬਾਜ਼ੀ ਵਿੱਚ ਦੁਨੀਆ ਭਰ ਵਿੱਚ ਨਾਮ ਕਮਾਇਆ। ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ ਦੇਸ਼ ਦੀ ਇੱਕ ਪ੍ਰਮੁੱਖ ਖੇਡ ਨਰਸਰੀ ਵਜੋਂ ਨੌਜਵਾਨਾਂ ਵਿੱਚ ਬੇਮਿਸਾਲ ਤਾਕਤ, ਅਨੁਸ਼ਾਸਨ ਅਤੇ ਜਿੱਤ ਦਾ ਜਜ਼ਬਾ ਭਰਦਾ ਹੈ।"
    },
    {
        "num": 503,
        "title_en": "Machine Gun Companies and Battalion",
        "title_hi": "मशीन गन कंपनियां और बटालियन",
        "title_pa": "ਮਸ਼ੀਨ ਗਨ ਕੰਪਨੀਆਂ ਅਤੇ ਬਟਾਲੀਅਨ",
        "category_en": "Beyond Battle Fd",
        "category_hi": "जंगी मैदान से परे",
        "category_pa": "ਜੰਗੀ ਮੈਦਾਨ ਤੋਂ ਪਰੇ",
        "summary_en": "Following World War I reorganisation, firepower within infantry battalions was dramatically upgraded by converting Delta Companies into specialised Machine Gun Companies. Equipped with Vickers .303 machine guns, these units provided devastating continuous fire support in critical battles. During World War II, dedicated Machine Gun Battalions of the Sikh Regiment served with unmatched distinction across the Western Desert, Middle East, and Burma. Their masterly gunnery, tactical mobility, and heroic steadfastness under enemy artillery barrages cemented the reputation of Sikh machine gunners as formidable pillars of infantry combat power.",
        "summary_hi": "प्रथम विश्व युद्ध के बाद सेना के पुनर्गठन के दौरान इन्फैंट्री बटालियनों की मारक क्षमता बढ़ाने के लिए डेल्टा कंपनियों को विशिष्ट मशीन गन कंपनियों में बदला गया। विकर्स .303 मशीन गन से लैस इन टुकड़ियों ने युद्ध के मैदान में अचूक अग्नि-समर्थन प्रदान किया। द्वितीय विश्व युद्ध में सिख रेजिमेंट की विशेष मशीन गन बटालियनों ने उत्तरी अफ्रीका, मध्य पूर्व और बर्मा के मोर्चों पर असाधारण पराक्रम दिखाया। उनकी अचूक निशानेबाजी और सामरिक गतिशीलता ने सिख मशीन गन दस्तों को पैदल सेना की मारक क्षमता का सबसे मजबूत आधार बना दिया।",
        "summary_pa": "ਪਹਿਲੇ ਵਿਸ਼ਵ ਯੁੱਧ ਤੋਂ ਬਾਅਦ ਫੌਜ ਦੇ ਪੁਨਰਗਠਨ ਦੌਰਾਨ ਬਟਾਲੀਅਨਾਂ ਦੀ ਫਾਇਰ ਪਾਵਰ ਵਧਾਉਣ ਲਈ ਡੈਲਟਾ ਕੰਪਨੀਆਂ ਨੂੰ ਵਿਸ਼ੇਸ਼ ਮਸ਼ੀਨ ਗਨ ਕੰਪਨੀਆਂ ਵਿੱਚ ਤਬਦੀਲ ਕੀਤਾ ਗਿਆ। ਵਿਕਰਸ .303 ਮਸ਼ੀਨ ਗਨਾਂ ਨਾਲ ਲੈਸ ਇਨ੍ਹਾਂ ਦਸਤਿਆਂ ਨੇ ਮੈਦਾਨ-ਏ-ਜੰਗ ਵਿੱਚ ਬੇਮਿਸਾਲ ਮਦਦ ਦਿੱਤੀ। ਦੂਜੇ ਵਿਸ਼ਵ ਯੁੱਧ ਦੌਰਾਨ ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦੀਆਂ ਮਸ਼ੀਨ ਗਨ ਬਟਾਲੀਅਨਾਂ ਨੇ ਉੱਤਰੀ ਅਫਰੀਕਾ, ਮੱਧ ਪੂਰਬ ਅਤੇ ਬਰਮਾ ਵਿੱਚ ਬਹਾਦਰੀ ਨਾਲ ਦੁਸ਼ਮਣ ਦੇ ਛੱਕੇ ਛੁਡਾਏ। ਉਨ੍ਹਾਂ ਦੀ ਅਚੂਕ ਨਿਸ਼ਾਨੇਬਾਜ਼ੀ ਅਤੇ ਦਲੇਰੀ ਨੇ ਸਿੱਖ ਮਸ਼ੀਨ ਗਨਰਾਂ ਨੂੰ ਜੰਗ ਦਾ ਅਹਿਮ ਥੰਮ੍ਹ ਬਣਾਇਆ।"
    },
    {
        "num": 504,
        "title_en": "Bonding at Sea and Air",
        "title_hi": "जल और नभ में अटूट बंधन",
        "title_pa": "ਸਮੁੰਦਰ ਅਤੇ ਅਸਮਾਨ ਵਿੱਚ ਸਾਂਝ",
        "category_en": "Beyond Battle Fd",
        "category_hi": "जंगी मैदान से परे",
        "category_pa": "ਜੰਗੀ ਮੈਦਾਨ ਤੋਂ ਪਰੇ",
        "summary_en": "The Sikh Regiment cherishes a unique inter-service brotherhood with the Indian Navy and Air Force. Its naval affiliation began in 1888 with the torpedo boat 'The Sikh' and was reaffirmed by affiliating with the modern guided-missile destroyer INS Mysore. In the skies, the Regiment is proudly affiliated with the Indian Air Force's No. 34 Squadron, the 'Hunters'. These tri-service bonds are celebrated through joint training exercises, ceremonial personnel exchanges, and mutual operational camaraderie, symbolizing integrated national defense, inter-service synergy, and shared martial pride across land, sea, and air.",
        "summary_hi": "सिख रेजिमेंट का भारतीय नौसेना और वायु सेना के साथ एक विशिष्ट और ऐतिहासिक त्रि-सेवा बंधन है। नौसेना के साथ इसका संबंध 1888 में टॉरपीडो बोट 'द सिख' से शुरू हुआ और आधुनिक समय में निर्देशित-मिसाइल विध्वंसक पोत 'आईएनएस मैसूर' के साथ इसे औपचारिक मान्यता मिली। वायु सेना में रेजिमेंट का संबद्धता नंबर 34 स्क्वाड्रन ('हंटर्स') के साथ है। यह गहरा तालमेल संयुक्त युद्धाभ्यासों, औपचारिक आदान-प्रदान और आपसी सहयोग के माध्यम से थल, जल और नभ में देश की अखंड सुरक्षा का प्रतीक है।",
        "summary_pa": "ਸਿੱਖ ਰੈਜੀਮੈਂਟ ਦਾ ਭਾਰਤੀ ਜਲ ਸੈਨਾ ਅਤੇ ਹਵਾਈ ਫੌਜ ਨਾਲ ਇੱਕ ਵਿਲੱਖਣ ਅਤੇ ਇਤਿਹਾਸਕ ਸਾਂਝ ਹੈ। ਜਲ ਸੈਨਾ ਨਾਲ ਇਸਦਾ ਸਬੰਧ 1888 ਵਿੱਚ ਟਾਰਪੀਡੋ ਕਿਸ਼ਤੀ 'ਦ ਸਿੱਖ' ਤੋਂ ਸ਼ੁਰੂ ਹੋਇਆ ਅਤੇ ਆਧੁਨਿਕ ਮਿਜ਼ਾਈਲ ਵਿਨਾਸ਼ਕਾਰੀ ਜਹਾਜ਼ 'ਆਈਐਨਐਸ ਮੈਸੂਰ' ਨਾਲ ਪੱਕਾ ਹੋਇਆ। ਹਵਾਈ ਫੌਜ ਵਿੱਚ ਰੈਜੀਮੈਂਟ ਦੀ ਸਾਂਝ ਨੰਬਰ 34 ਸਕੁਐਡਰਨ ('ਹੰਟਰਜ਼') ਨਾਲ ਹੈ। ਇਹ ਤਿੰਨੇ ਸੈਨਾਵਾਂ ਦਾ ਆਪਸੀ ਤਾਲਮੇਲ ਸਾਂਝੇ ਅਭਿਆਸਾਂ ਅਤੇ ਸਨਮਾਨ ਸਮਾਗਮਾਂ ਰਾਹੀਂ ਜ਼ਮੀਨ, ਸਮੁੰਦਰ ਅਤੇ ਅਸਮਾਨ ਵਿੱਚ ਦੇਸ਼ ਦੀ ਮਜ਼ਬੂਤ ਰੱਖਿਆ ਨੂੰ ਦਰਸਾਉਂਦਾ ਹੈ।"
    },
    {
        "num": 505,
        "title_en": "9th Battalion The Sikh Regiment",
        "title_hi": "9वीं बटालियन द सिख रेजिमेंट",
        "title_pa": "9ਵੀਂ ਬਟਾਲੀਅਨ ਦ ਸਿੱਖ ਰੈਜੀਮੈਂਟ",
        "category_en": "Beyond Battle Fd",
        "category_hi": "जंगी मैदान से परे",
        "category_pa": "ਜੰਗੀ ਮੈਦਾਨ ਤੋਂ ਪਰੇ",
        "summary_en": "Raised on 01 April 1964 at Meerut under Major (later Maj Gen) RT Morlin and Lt Col Harbans Singh, 9 SIKH has forged a stellar record of valor and sacrifice. The battalion served with great distinction in the 1965 Indo-Pak War, in high-altitude counter-insurgency operations in Nagaland and Mizoram, and in the 1971 war where it captured enemy posts with supreme grit. In Punjab, Kashmir, and on the Line of Control, 9 Sikh demonstrated exemplary combat readiness, earning numerous gallantry awards including Vir Chakras, Sena Medals, and COAS Unit Citations for steadfast devotion to duty.",
        "summary_hi": "9वीं सिख की स्थापना 1 अप्रैल 1964 को मेरठ में मेजर (बाद में मेजर जनरल) आर.टी. मोरलीन और लेफ्टिनेंट कर्नल हरबंस सिंह के नेतृत्व में हुई थी। बटालियन ने 1965 के भारत-पाक युद्ध, नागालैंड और मिजोरम में उग्रवाद विरोधी अभियानों तथा 1971 के युद्ध में अद्वितीय वीरता का परिचय दिया और दुश्मन की कई चौकियों पर कब्जा किया। पंजाब, जम्मू-कश्मीर और नियंत्रण रेखा पर तैनात रहते हुए 9 सिख ने कई वीर चक्र, सेना मेडल और सेना प्रमुख यूनिट प्रशस्ति पत्र अर्जित कर रेजिमेंट का गौरव बढ़ाया।",
        "summary_pa": "9 ਸਿੱਖ ਦੀ ਸਥਾਪਨਾ 1 ਅਪ੍ਰੈਲ 1964 ਨੂੰ ਮੇਰਠ ਵਿਖੇ ਮੇਜਰ (ਬਾਅਦ ਵਿੱਚ ਮੇਜਰ ਜਨਰਲ) ਆਰ.ਟੀ. ਮੋਰਲਿਨ ਅਤੇ ਲੈਫਟੀਨੈਂਟ ਕਰਨਲ ਹਰਬੰਸ ਸਿੰਘ ਦੀ ਅਗਵਾਈ ਵਿੱਚ ਹੋਈ। ਬਟਾਲੀਅਨ ਨੇ 1965 ਦੀ ਜੰਗ, ਨਾਗਾਲੈਂਡ ਤੇ ਮਿਜ਼ੋਰਮ ਵਿੱਚ ਅੱਤਵਾਦ ਵਿਰੋਧੀ ਕਾਰਵਾਈਆਂ ਅਤੇ 1971 ਦੀ ਭਾਰਤ-ਪਾਕਿ ਜੰਗ ਵਿੱਚ ਸ਼ਾਨਦਾਰ ਬਹਾਦਰੀ ਦਾ ਪ੍ਰਦਰਸ਼ਨ ਕੀਤਾ। ਪੰਜਾਬ, ਕਸ਼ਮੀਰ ਅਤੇ ਐਲਓਸੀ 'ਤੇ ਤਾਇਨਾਤ ਰਹਿੰਦਿਆਂ 9 ਸਿੱਖ ਨੇ ਕਈ ਵੀਰ ਚੱਕਰ, ਸੈਨਾ ਮੈਡਲ ਅਤੇ ਫੌਜ ਮੁਖੀ ਪ੍ਰਸ਼ੰਸਾ ਪੱਤਰ ਹਾਸਲ ਕਰਕੇ ਰੈਜੀਮੈਂਟ ਦਾ ਨਾਮ ਰੌਸ਼ਨ ਕੀਤਾ।"
    }
]

# Translation helpers
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
    print("Updating Beyond Battle Fd HTML pages (EN, HI, PA)...")
    for item in EXHIBITS_DATA:
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
                
        # Back to Home for EN
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
<strong>कलाकार:</strong> सिख रेजिमेंटल सेंटर<br/>
<strong>वर्ष:</strong> ऐतिहासिक<br/>"""
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
                    trans_p = re.sub(r'\bSIKH\b', 'सिख', trans_p, flags=re.I)
                    trans_p = re.sub(r'\bSIKHS\b', 'सिख', trans_p, flags=re.I)
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
<strong>ਕਲਾਕਾਰ:</strong> ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਸੈਂਟਰ<br/>
<strong>ਸਾਲ:</strong> ਇਤਿਹਾਸਕ<br/>"""
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
                    trans_p = re.sub(r'\bSIKH\b', 'ਸਿੱਖ', trans_p, flags=re.I)
                    trans_p = re.sub(r'\bSIKHS\b', 'ਸਿੱਖ', trans_p, flags=re.I)
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
    print("All Beyond Battle Fd HTML pages generated successfully!")

def update_dropdowns():
    print("Updating dropdown-6 in index_en.html, index_hi.html, index_pa.html...")
    
    # 1. English Dropdown
    with open("index_en.html", "r", encoding="utf-8") as f:
        soup_en = BeautifulSoup(f.read(), "html.parser")
    dd_en = soup_en.find("div", id="dropdown-6")
    if dd_en:
        dd_en_html = """<div class="nested-dropdown">
<button class="nested-btn" onclick="toggleNestedDropdown(event, 'nested-181')">
    Regimental Icons
    <svg class="arrow-icon" fill="none" height="12" stroke="currentColor" stroke-width="3" style="transition: transform 0.2s ease;" viewbox="0 0 24 24" width="12">
        <polyline points="9 18 15 12 9 6"></polyline>
    </svg>
</button>
<div class="nested-dropdown-content" id="nested-181">
    <a href="art507.html">HH Maharaja Yadavindra Singh</a>
    <a href="art508.html">Lt Gen Harbakhsh Singh, VrC</a>
    <a href="art509.html">General RA Savory, KCIE, CB, DSO, MC</a>
</div>
</div>
<a href="art501.html">History of Sikh Regimental Band</a>
<a href="art502.html">Sporting Prowess of the Sikhs</a>
<a href="art503.html">Machine Gun Companies and Battalion</a>
<a href="art504.html">Bonding at Sea and Air</a>
<a href="art505.html">9th Battalion The Sikh Regiment</a>"""
        dd_en.clear()
        dd_en.append(BeautifulSoup(dd_en_html, "html.parser"))
        with open("index_en.html", "w", encoding="utf-8") as f:
            f.write(str(soup_en))

    # 2. Hindi Dropdown
    with open("index_hi.html", "r", encoding="utf-8") as f:
        soup_hi = BeautifulSoup(f.read(), "html.parser")
    dd_hi = soup_hi.find("div", id="dropdown-6")
    if dd_hi:
        dd_hi_html = """<div class="nested-dropdown">
<button class="nested-btn" onclick="toggleNestedDropdown(event, 'nested-181')">
    रेजिमेंटल प्रतीक
    <svg class="arrow-icon" fill="none" height="12" stroke="currentColor" stroke-width="3" style="transition: transform 0.2s ease;" viewbox="0 0 24 24" width="12">
        <polyline points="9 18 15 12 9 6"></polyline>
    </svg>
</button>
<div class="nested-dropdown-content" id="nested-181">
    <a href="art507_hi.html">महाराजा यादविंद्र सिंह</a>
    <a href="art508_hi.html">लेफ्टिनेंट जनरल हरबख्श सिंह, वीआरसी</a>
    <a href="art509_hi.html">जनरल आर.ए. सेवरी, केसीआईई, सीबी, डीएसओ, एमसी</a>
</div>
</div>
<a href="art501_hi.html">सिख रेजिमेंटल बैंड का इतिहास</a>
<a href="art502_hi.html">सिखों की खेल उत्कृष्टता</a>
<a href="art503_hi.html">मशीन गन कंपनियां और बटालियन</a>
<a href="art504_hi.html">जल और नभ में अटूट बंधन</a>
<a href="art505_hi.html">9वीं बटालियन द सिख रेजिमेंट</a>"""
        dd_hi.clear()
        dd_hi.append(BeautifulSoup(dd_hi_html, "html.parser"))
        with open("index_hi.html", "w", encoding="utf-8") as f:
            f.write(str(soup_hi))

    # 3. Punjabi Dropdown
    with open("index_pa.html", "r", encoding="utf-8") as f:
        soup_pa = BeautifulSoup(f.read(), "html.parser")
    dd_pa = soup_pa.find("div", id="dropdown-6")
    if dd_pa:
        dd_pa_html = """<div class="nested-dropdown">
<button class="nested-btn" onclick="toggleNestedDropdown(event, 'nested-181')">
    ਰੈਜੀਮੈਂਟਲ ਆਈਕਨ
    <svg class="arrow-icon" fill="none" height="12" stroke="currentColor" stroke-width="3" style="transition: transform 0.2s ease;" viewbox="0 0 24 24" width="12">
        <polyline points="9 18 15 12 9 6"></polyline>
    </svg>
</button>
<div class="nested-dropdown-content" id="nested-181">
    <a href="art507_pa.html">ਮਹਾਰਾਜਾ ਯਾਦਵਿੰਦਰ ਸਿੰਘ</a>
    <a href="art508_pa.html">ਲੈਫਟੀਨੈਂਟ ਜਨਰਲ ਹਰਬਖ਼ਸ਼ ਸਿੰਘ, ਵੀਆਰਸੀ</a>
    <a href="art509_pa.html">ਜਨਰਲ ਆਰ.ਏ. ਸੇਵਰੀ, ਕੇਸੀਆਈਈ, ਸੀਬੀ, ਡੀਐਸਓ, ਐਮਸੀ</a>
</div>
</div>
<a href="art501_pa.html">ਸਿੱਖ ਰੈਜੀਮੈਂਟਲ ਬੈਂਡ ਦਾ ਇਤਿਹਾਸ</a>
<a href="art502_pa.html">ਸਿੱਖਾਂ ਦੀ ਖੇਡ ਪ੍ਰਤਿਭਾ</a>
<a href="art503_pa.html">ਮਸ਼ੀਨ ਗਨ ਕੰਪਨੀਆਂ ਅਤੇ ਬਟਾਲੀਅਨ</a>
<a href="art504_pa.html">ਸਮੁੰਦਰ ਅਤੇ ਅਸਮਾਨ ਵਿੱਚ ਸਾਂਝ</a>
<a href="art505_pa.html">9ਵੀਂ ਬਟਾਲੀਅਨ ਦ ਸਿੱਖ ਰੈਜੀਮੈਂਟ</a>"""
        dd_pa.clear()
        dd_pa.append(BeautifulSoup(dd_pa_html, "html.parser"))
        with open("index_pa.html", "w", encoding="utf-8") as f:
            f.write(str(soup_pa))

    print("Dropdown navigation synchronized across all three language portals.")

async def generate_smart_audios():
    print("Synthesizing ~100-word smart audio recitations in English, Hindi, and Punjabi...")
    os.makedirs("assets/audio", exist_ok=True)
    os.makedirs("assets/audio_hi", exist_ok=True)
    os.makedirs("assets/audio_pa", exist_ok=True)
    
    for item in EXHIBITS_DATA:
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
    print("=== STARTING BEYOND BATTLE FD OVERHAUL ===")
    update_html_pages()
    update_dropdowns()
    asyncio.run(generate_smart_audios())
    print("=== BEYOND BATTLE FD OVERHAUL COMPLETED SUCCESSFULLY! ===")

if __name__ == "__main__":
    main()
