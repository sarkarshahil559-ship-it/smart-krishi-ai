from flask import Flask, render_template, request
import webbrowser
from threading import Timer
import pickle
import sys
import os
import urllib.request
import urllib.parse
import urllib.error
import json
from math import radians, sin, cos, sqrt, atan2


# =====================================================
# VISION FOLDER
# =====================================================

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "vision"
    )
)

from vision import analyze_crop_image


# =====================================================
# FLASK APP
# =====================================================

app = Flask(__name__)


# =====================================================
# SUPPORTED LANGUAGES
# =====================================================

SUPPORTED_LANGUAGES = [
    "en", "bn", "hi", "ta", "te",
    "mr", "gu", "kn", "pa"
]


# =====================================================
# RESULT TEXT TRANSLATIONS
# =====================================================

TEXT = {

    "en": {
        "unknown": "Unknown",
        "not_available": "Not available",
        "storage_facility": "Storage Facility",

        "high_humidity":
            "🌧️ High humidity: monitor crops for fungal problems.",
        "low_humidity":
            "💧 Low humidity: check soil moisture regularly.",
        "moderate_humidity":
            "🌱 Humidity is in a moderate range.",

        "high_temperature":
            "☀️ High temperature: provide adequate irrigation.",
        "low_temperature":
            "❄️ Low temperature: protect temperature-sensitive crops.",
        "suitable_temperature":
            "🌤️ Temperature is suitable for many crops.",

        "strong_wind":
            "💨 Strong wind: check plants and provide support if needed.",

        "irrigation_recommended":
            "💧 Irrigation Recommended",
        "moderate_moisture":
            "🌿 Moderate Moisture",
        "irrigation_not_needed":
            "✅ Irrigation Not Immediately Needed",

        "low_soil_moisture":
            "🌱 Soil moisture is low. Irrigation may be needed.",
        "moderate_soil_moisture":
            "🌿 Soil moisture is moderate. Monitor the soil before irrigation.",
        "high_soil_moisture":
            "💧 Soil moisture is relatively high. Avoid unnecessary irrigation.",

        "hot_irrigation":
            "☀️ High temperature detected. Check soil moisture more frequently.",
        "cold_irrigation":
            "❄️ Low temperature detected. Avoid unnecessary watering.",
        "moderate_temperature":
            "🌤️ Temperature is in a moderate range.",

        "high_irrigation_humidity":
            "🌧️ High humidity detected. Avoid over-irrigation.",
        "low_irrigation_humidity":
            "💨 Low humidity detected. Plants may lose water faster.",
        "moderate_irrigation_humidity":
            "💧 Humidity is in a moderate range.",

        "heavy_rain":
            "🌧️ Significant rainfall detected. Reduce or delay irrigation if soil is already moist.",
        "some_rain":
            "🌦️ Some rainfall is present. Check soil moisture before watering.",
        "no_rain":
            "☀️ No significant rainfall reported. Monitor soil moisture regularly.",

        "sort_storage":
            "🧺 Sort and remove damaged or diseased produce before storage.",
        "clean_storage":
            "🧼 Keep storage containers, floors and tools clean and dry.",
        "air_storage":
            "📦 Avoid overfilling containers and allow proper air circulation.",
        "grain_dry":
            "🌾 Grain crops should be properly dried before long-term storage.",
        "grain_protect":
            "💧 Protect grains from excess moisture, insects and rodents.",
        "potato_store":
            "🥔 Store potatoes in a cool, dark and well-ventilated place.",
        "potato_sun":
            "☀️ Keep potatoes away from direct sunlight.",
        "onion_store":
            "🧅 Onion should be properly cured and stored in a dry, ventilated place.",
        "onion_humidity":
            "💧 Avoid excess humidity because it can encourage spoilage.",
        "fresh_handle":
            "🥬 Handle fresh produce gently to reduce bruising and damage.",
        "fresh_pack":
            "📦 Use suitable ventilated packaging and inspect regularly.",

        "storage_hot":
            "☀️ Storage temperature is very high. Move produce to a cooler suitable environment.",
        "storage_cold":
            "❄️ Storage temperature is very low. Check whether the crop is suitable for this condition.",
        "storage_temp_monitor":
            "🌡️ Monitor storage temperature regularly.",

        "storage_humidity_high":
            "💧 High storage humidity detected. Improve ventilation and reduce moisture exposure.",
        "storage_humidity_low":
            "🏜️ Low storage humidity detected. Monitor produce for excessive moisture loss.",
        "storage_humidity_moderate":
            "💧 Storage humidity is in a moderate range.",

        "long_storage":
            "📅 Long-term storage planned. Inspect produce regularly for spoilage, pests and quality changes.",
        "medium_storage":
            "📅 Medium-term storage planned. Regular inspection is recommended.",
        "short_storage":
            "📅 Short-term storage planned. Keep produce clean, protected and properly ventilated.",

        "storage_crop_search":
            "Search requested for {crop}. Confirm crop acceptance with the facility.",
        "address_unavailable":
            "Address not available",
        "contact_unavailable":
            "Not publicly available",
        "confirm_contact":
            "Contact facility to confirm",
        "available":
            "Available",
        "check_availability":
            "Check availability",

        "market_config":
            "Government Mandi API is not configured yet. No fake market price has been shown.",
        "market_no_data":
            "No reliable mandi price was found for the selected crop and location.",
        "market_data_found":
            "Available mandi data found at {level} level.",
        "market_best":
            "Best available option: {market}. Modal price: {price}.",
        "market_area_note":
            " No exact area filter was used for '{city}'. Showing available mandis from the selected district/state level.",
        "market_load_failed":
            "Market data could not be loaded. Please try again later.",

        "visual_note":
            "Visual analysis only."
    },


    "bn": {
        "unknown": "অজানা",
        "not_available": "উপলব্ধ নয়",
        "storage_facility": "স্টোরেজ সুবিধা",

        "high_humidity":
            "🌧️ বাতাসে আর্দ্রতা বেশি। ফসলে ছত্রাকজনিত সমস্যা লক্ষ্য করুন।",
        "low_humidity":
            "💧 বাতাসের আর্দ্রতা কম। মাটির আর্দ্রতা নিয়মিত পরীক্ষা করুন।",
        "moderate_humidity":
            "🌱 বাতাসের আর্দ্রতা মাঝারি মাত্রায় রয়েছে।",

        "high_temperature":
            "☀️ তাপমাত্রা বেশি। পর্যাপ্ত সেচের ব্যবস্থা করুন।",
        "low_temperature":
            "❄️ তাপমাত্রা কম। কম তাপমাত্রায় সংবেদনশীল ফসল রক্ষা করুন।",
        "suitable_temperature":
            "🌤️ তাপমাত্রা অনেক ফসলের জন্য উপযুক্ত।",

        "strong_wind":
            "💨 বাতাসের গতি বেশি। গাছপালা পরীক্ষা করুন এবং প্রয়োজনে সাপোর্ট দিন।",

        "irrigation_recommended":
            "💧 সেচ দেওয়ার পরামর্শ দেওয়া হচ্ছে",
        "moderate_moisture":
            "🌿 মাটির আর্দ্রতা মাঝারি",
        "irrigation_not_needed":
            "✅ এই মুহূর্তে সেচের প্রয়োজন নেই",

        "low_soil_moisture":
            "🌱 মাটির আর্দ্রতা কম। সেচের প্রয়োজন হতে পারে।",
        "moderate_soil_moisture":
            "🌿 মাটির আর্দ্রতা মাঝারি। সেচ দেওয়ার আগে মাটি পর্যবেক্ষণ করুন।",
        "high_soil_moisture":
            "💧 মাটির আর্দ্রতা তুলনামূলক বেশি। অপ্রয়োজনীয় সেচ এড়িয়ে চলুন।",

        "hot_irrigation":
            "☀️ তাপমাত্রা বেশি। মাটির আর্দ্রতা আরও ঘন ঘন পরীক্ষা করুন।",
        "cold_irrigation":
            "❄️ তাপমাত্রা কম। অপ্রয়োজনীয় জল দেওয়া এড়িয়ে চলুন।",
        "moderate_temperature":
            "🌤️ তাপমাত্রা মাঝারি মাত্রায় রয়েছে।",

        "high_irrigation_humidity":
            "🌧️ বাতাসের আর্দ্রতা বেশি। অতিরিক্ত সেচ এড়িয়ে চলুন।",
        "low_irrigation_humidity":
            "💨 বাতাসের আর্দ্রতা কম। গাছ দ্রুত জল হারাতে পারে।",
        "moderate_irrigation_humidity":
            "💧 বাতাসের আর্দ্রতা মাঝারি মাত্রায় রয়েছে।",

        "heavy_rain":
            "🌧️ উল্লেখযোগ্য বৃষ্টিপাত হয়েছে। মাটি ভেজা থাকলে সেচ কমিয়ে দিন বা কিছু সময়ের জন্য বন্ধ রাখুন।",
        "some_rain":
            "🌦️ কিছু বৃষ্টিপাত হয়েছে। জল দেওয়ার আগে মাটির আর্দ্রতা পরীক্ষা করুন।",
        "no_rain":
            "☀️ উল্লেখযোগ্য বৃষ্টিপাত নেই। নিয়মিত মাটির আর্দ্রতা পরীক্ষা করুন।",

        "sort_storage":
            "🧺 স্টোরেজের আগে ক্ষতিগ্রস্ত বা রোগাক্রান্ত ফসল আলাদা করে ফেলুন।",
        "clean_storage":
            "🧼 স্টোরেজের পাত্র, মেঝে ও সরঞ্জাম পরিষ্কার এবং শুকনো রাখুন।",
        "air_storage":
            "📦 পাত্র অতিরিক্ত ভরবেন না এবং পর্যাপ্ত বায়ু চলাচল নিশ্চিত করুন।",
        "grain_dry":
            "🌾 দীর্ঘমেয়াদি সংরক্ষণের আগে শস্য ভালোভাবে শুকিয়ে নিন।",
        "grain_protect":
            "💧 অতিরিক্ত আর্দ্রতা, পোকামাকড় ও ইঁদুর থেকে শস্য রক্ষা করুন।",
        "potato_store":
            "🥔 আলু ঠান্ডা, অন্ধকার ও বায়ু চলাচলযুক্ত স্থানে রাখুন।",
        "potato_sun":
            "☀️ আলুকে সরাসরি সূর্যের আলো থেকে দূরে রাখুন।",
        "onion_store":
            "🧅 পেঁয়াজ ভালোভাবে শুকিয়ে শুকনো ও বায়ু চলাচলযুক্ত স্থানে রাখুন।",
        "onion_humidity":
            "💧 অতিরিক্ত আর্দ্রতা এড়িয়ে চলুন, কারণ এতে পচন বাড়তে পারে।",
        "fresh_handle":
            "🥬 তাজা ফসল সাবধানে ধরুন যাতে আঘাত বা ক্ষতি কম হয়।",
        "fresh_pack":
            "📦 উপযুক্ত বায়ু চলাচলযুক্ত প্যাকেজিং ব্যবহার করুন এবং নিয়মিত পরীক্ষা করুন।",

        "storage_hot":
            "☀️ স্টোরেজের তাপমাত্রা খুব বেশি। ফসলকে আরও ঠান্ডা উপযুক্ত স্থানে রাখুন।",
        "storage_cold":
            "❄️ স্টোরেজের তাপমাত্রা খুব কম। এই অবস্থার জন্য ফসলটি উপযুক্ত কিনা পরীক্ষা করুন।",
        "storage_temp_monitor":
            "🌡️ নিয়মিত স্টোরেজের তাপমাত্রা পর্যবেক্ষণ করুন।",

        "storage_humidity_high":
            "💧 স্টোরেজে আর্দ্রতা বেশি। বায়ু চলাচল বাড়ান এবং আর্দ্রতার সংস্পর্শ কমান।",
        "storage_humidity_low":
            "🏜️ স্টোরেজের আর্দ্রতা কম। অতিরিক্ত জল হারানোর জন্য ফসল পর্যবেক্ষণ করুন।",
        "storage_humidity_moderate":
            "💧 স্টোরেজের আর্দ্রতা মাঝারি মাত্রায় রয়েছে।",

        "long_storage":
            "📅 দীর্ঘমেয়াদি সংরক্ষণ পরিকল্পনা করা হয়েছে। পচন, পোকা ও গুণমানের পরিবর্তনের জন্য নিয়মিত পরীক্ষা করুন।",
        "medium_storage":
            "📅 মাঝারি মেয়াদের সংরক্ষণ পরিকল্পনা করা হয়েছে। নিয়মিত পরীক্ষা করার পরামর্শ দেওয়া হচ্ছে।",
        "short_storage":
            "📅 স্বল্পমেয়াদি সংরক্ষণ পরিকল্পনা করা হয়েছে। ফসল পরিষ্কার, সুরক্ষিত ও বায়ু চলাচলযুক্ত রাখুন।",

        "storage_crop_search":
            "{crop}-এর জন্য অনুসন্ধান করা হয়েছে। ফসল গ্রহণ করে কিনা স্টোরেজ কর্তৃপক্ষের সঙ্গে নিশ্চিত করুন।",
        "address_unavailable":
            "ঠিকানা উপলব্ধ নয়",
        "contact_unavailable":
            "সর্বজনীনভাবে উপলব্ধ নয়",
        "confirm_contact":
            "নিশ্চিত করতে স্টোরেজ কর্তৃপক্ষের সঙ্গে যোগাযোগ করুন",
        "available":
            "উপলব্ধ",
        "check_availability":
            "উপলব্ধতা পরীক্ষা করুন",

        "market_config":
            "সরকারি মান্ডি API এখনও কনফিগার করা হয়নি। কোনো ভুয়া বাজারদর দেখানো হয়নি।",
        "market_no_data":
            "নির্বাচিত ফসল ও এলাকার জন্য নির্ভরযোগ্য মান্ডি মূল্য পাওয়া যায়নি।",
        "market_data_found":
            "{level} স্তরে উপলব্ধ মান্ডি তথ্য পাওয়া গেছে।",
        "market_best":
            "সেরা উপলব্ধ বাজার: {market}। মডাল মূল্য: {price}।",
        "market_area_note":
            " '{city}'-এর জন্য কোনো exact area filter ব্যবহার করা হয়নি। নির্বাচিত district/state স্তরের উপলব্ধ মান্ডি দেখানো হচ্ছে।",
        "market_load_failed":
            "বাজারের তথ্য লোড করা যায়নি। পরে আবার চেষ্টা করুন।",

        "visual_note":
            "শুধুমাত্র ছবির দৃশ্যমান বিশ্লেষণ।"
    },


    "hi": {
        "unknown": "अज्ञात",
        "not_available": "उपलब्ध नहीं",
        "storage_facility": "भंडारण सुविधा",

        "high_humidity": "🌧️ नमी अधिक है। फसल में फंगल समस्या पर ध्यान दें।",
        "low_humidity": "💧 नमी कम है। मिट्टी की नमी नियमित रूप से जांचें।",
        "moderate_humidity": "🌱 नमी मध्यम स्तर पर है।",

        "high_temperature": "☀️ तापमान अधिक है। पर्याप्त सिंचाई करें।",
        "low_temperature": "❄️ तापमान कम है। संवेदनशील फसलों की सुरक्षा करें।",
        "suitable_temperature": "🌤️ तापमान कई फसलों के लिए उपयुक्त है।",

        "strong_wind": "💨 तेज हवा है। पौधों की जांच करें और जरूरत पड़ने पर सहारा दें।",

        "irrigation_recommended": "💧 सिंचाई की सलाह दी जाती है",
        "moderate_moisture": "🌿 मिट्टी की नमी मध्यम है",
        "irrigation_not_needed": "✅ अभी सिंचाई की आवश्यकता नहीं है",

        "low_soil_moisture": "🌱 मिट्टी की नमी कम है। सिंचाई की आवश्यकता हो सकती है।",
        "moderate_soil_moisture": "🌿 मिट्टी की नमी मध्यम है। सिंचाई से पहले मिट्टी जांचें।",
        "high_soil_moisture": "💧 मिट्टी की नमी अधिक है। अनावश्यक सिंचाई से बचें।",

        "hot_irrigation": "☀️ तापमान अधिक है। मिट्टी की नमी अधिक बार जांचें।",
        "cold_irrigation": "❄️ तापमान कम है। अनावश्यक पानी देने से बचें।",
        "moderate_temperature": "🌤️ तापमान मध्यम है।",

        "high_irrigation_humidity": "🌧️ नमी अधिक है। अधिक सिंचाई से बचें।",
        "low_irrigation_humidity": "💨 नमी कम है। पौधे तेजी से पानी खो सकते हैं।",
        "moderate_irrigation_humidity": "💧 नमी मध्यम स्तर पर है।",

        "heavy_rain": "🌧️ पर्याप्त वर्षा हुई है। मिट्टी गीली होने पर सिंचाई कम या स्थगित करें।",
        "some_rain": "🌦️ कुछ वर्षा हुई है। पानी देने से पहले मिट्टी की नमी जांचें।",
        "no_rain": "☀️ महत्वपूर्ण वर्षा नहीं हुई। मिट्टी की नमी नियमित रूप से जांचें।",

        "sort_storage": "🧺 भंडारण से पहले खराब या रोगग्रस्त फसल अलग करें।",
        "clean_storage": "🧼 भंडारण के कंटेनर, फर्श और उपकरण साफ व सूखे रखें।",
        "air_storage": "📦 कंटेनरों को अधिक न भरें और हवा का उचित प्रवाह रखें।",
        "grain_dry": "🌾 लंबे समय के भंडारण से पहले अनाज को अच्छी तरह सुखाएं।",
        "grain_protect": "💧 अनाज को अधिक नमी, कीड़ों और चूहों से बचाएं।",
        "potato_store": "🥔 आलू को ठंडी, अंधेरी और हवादार जगह पर रखें।",
        "potato_sun": "☀️ आलू को सीधी धूप से दूर रखें।",
        "onion_store": "🧅 प्याज को अच्छी तरह सुखाकर सूखी और हवादार जगह पर रखें।",
        "onion_humidity": "💧 अधिक नमी से बचें क्योंकि इससे खराब होने की संभावना बढ़ सकती है।",
        "fresh_handle": "🥬 ताजा फसल को सावधानी से संभालें ताकि नुकसान कम हो।",
        "fresh_pack": "📦 उचित हवादार पैकेजिंग का उपयोग करें और नियमित जांच करें।",

        "storage_hot": "☀️ भंडारण तापमान बहुत अधिक है। फसल को ठंडी उपयुक्त जगह पर रखें।",
        "storage_cold": "❄️ भंडारण तापमान बहुत कम है। जांचें कि फसल इस स्थिति के लिए उपयुक्त है या नहीं।",
        "storage_temp_monitor": "🌡️ भंडारण तापमान की नियमित निगरानी करें।",

        "storage_humidity_high": "💧 भंडारण में नमी अधिक है। वेंटिलेशन बढ़ाएं और नमी कम करें।",
        "storage_humidity_low": "🏜️ भंडारण में नमी कम है। अधिक नमी खोने के लिए फसल की निगरानी करें।",
        "storage_humidity_moderate": "💧 भंडारण की नमी मध्यम स्तर पर है।",

        "long_storage": "📅 लंबे समय का भंडारण है। खराब होने, कीट और गुणवत्ता परिवर्तन की नियमित जांच करें।",
        "medium_storage": "📅 मध्यम अवधि का भंडारण है। नियमित जांच की सलाह दी जाती है।",
        "short_storage": "📅 कम अवधि का भंडारण है। फसल को साफ, सुरक्षित और हवादार रखें।",

        "storage_crop_search": "{crop} के लिए खोज की गई है। सुविधा से फसल स्वीकार करने की पुष्टि करें।",
        "address_unavailable": "पता उपलब्ध नहीं है",
        "contact_unavailable": "सार्वजनिक रूप से उपलब्ध नहीं",
        "confirm_contact": "पुष्टि के लिए सुविधा से संपर्क करें",
        "available": "उपलब्ध",
        "check_availability": "उपलब्धता जांचें",

        "market_config": "सरकारी मंडी API अभी कॉन्फ़िगर नहीं है। कोई नकली बाजार मूल्य नहीं दिखाया गया है।",
        "market_no_data": "चयनित फसल और स्थान के लिए विश्वसनीय मंडी मूल्य नहीं मिला।",
        "market_data_found": "{level} स्तर पर उपलब्ध मंडी डेटा मिला।",
        "market_best": "सबसे अच्छा उपलब्ध बाजार: {market}। मॉडल मूल्य: {price}।",
        "market_area_note": " '{city}' के लिए exact area filter का उपयोग नहीं किया गया। चयनित district/state स्तर की मंडियां दिखाई जा रही हैं।",
        "market_load_failed": "बाजार डेटा लोड नहीं हो सका। बाद में फिर कोशिश करें।",

        "visual_note": "केवल दृश्य विश्लेषण।"
    },


    "ta": {
        "unknown": "தெரியவில்லை",
        "not_available": "கிடைக்கவில்லை",
        "storage_facility": "சேமிப்பு வசதி",
        "high_humidity": "🌧️ ஈரப்பதம் அதிகம். பூஞ்சை பிரச்சினைகளை கவனிக்கவும்.",
        "low_humidity": "💧 ஈரப்பதம் குறைவு. மண் ஈரப்பதத்தை தொடர்ந்து சரிபார்க்கவும்.",
        "moderate_humidity": "🌱 ஈரப்பதம் மிதமான நிலையில் உள்ளது.",
        "high_temperature": "☀️ வெப்பநிலை அதிகம். போதுமான நீர்ப்பாசனம் செய்யவும்.",
        "low_temperature": "❄️ வெப்பநிலை குறைவு. உணர்திறன் கொண்ட பயிர்களை பாதுகாக்கவும்.",
        "suitable_temperature": "🌤️ வெப்பநிலை பல பயிர்களுக்கு ஏற்றது.",
        "strong_wind": "💨 காற்று வேகம் அதிகம். செடிகளை சரிபார்க்கவும்.",
        "irrigation_recommended": "💧 நீர்ப்பாசனம் பரிந்துரைக்கப்படுகிறது",
        "moderate_moisture": "🌿 மண் ஈரப்பதம் மிதமானது",
        "irrigation_not_needed": "✅ உடனடி நீர்ப்பாசனம் தேவையில்லை",
        "low_soil_moisture": "🌱 மண் ஈரப்பதம் குறைவு. நீர்ப்பாசனம் தேவைப்படலாம்.",
        "moderate_soil_moisture": "🌿 மண் ஈரப்பதம் மிதமானது. நீர்ப்பாசனத்திற்கு முன் மண்ணை கவனிக்கவும்.",
        "high_soil_moisture": "💧 மண் ஈரப்பதம் அதிகம். தேவையற்ற நீர்ப்பாசனத்தை தவிர்க்கவும்.",
        "hot_irrigation": "☀️ வெப்பநிலை அதிகம். மண் ஈரப்பதத்தை அடிக்கடி சரிபார்க்கவும்.",
        "cold_irrigation": "❄️ வெப்பநிலை குறைவு. தேவையற்ற நீர் வழங்குவதை தவிர்க்கவும்.",
        "moderate_temperature": "🌤️ வெப்பநிலை மிதமானது.",
        "high_irrigation_humidity": "🌧️ ஈரப்பதம் அதிகம். அதிக நீர்ப்பாசனத்தை தவிர்க்கவும்.",
        "low_irrigation_humidity": "💨 ஈரப்பதம் குறைவு. செடிகள் வேகமாக நீரை இழக்கலாம்.",
        "moderate_irrigation_humidity": "💧 ஈரப்பதம் மிதமானது.",
        "heavy_rain": "🌧️ குறிப்பிடத்தக்க மழை பெய்துள்ளது. மண் ஈரமாக இருந்தால் நீர்ப்பாசனத்தை குறைக்கவும்.",
        "some_rain": "🌦️ சில மழை உள்ளது. நீர் வழங்குவதற்கு முன் மண் ஈரப்பதத்தை சரிபார்க்கவும்.",
        "no_rain": "☀️ குறிப்பிடத்தக்க மழை இல்லை. மண் ஈரப்பதத்தை தொடர்ந்து கவனிக்கவும்.",
        "sort_storage": "🧺 சேமிப்புக்கு முன் சேதமடைந்த பயிர்களை பிரிக்கவும்.",
        "clean_storage": "🧼 சேமிப்பு பொருட்கள் மற்றும் கருவிகளை சுத்தமாகவும் உலர்ந்தும் வைத்திருக்கவும்.",
        "air_storage": "📦 கொள்கலன்களை அதிகமாக நிரப்ப வேண்டாம்; நல்ல காற்றோட்டம் இருக்கட்டும்.",
        "grain_dry": "🌾 நீண்டகால சேமிப்புக்கு முன் தானியங்களை நன்கு உலர்த்தவும்.",
        "grain_protect": "💧 தானியங்களை ஈரப்பதம், பூச்சிகள் மற்றும் எலிகளிலிருந்து பாதுகாக்கவும்.",
        "potato_store": "🥔 உருளைக்கிழங்கை குளிர்ந்த, இருண்ட மற்றும் காற்றோட்டமான இடத்தில் சேமிக்கவும்.",
        "potato_sun": "☀️ உருளைக்கிழங்கை நேரடி சூரிய ஒளியிலிருந்து விலக்கி வைக்கவும்.",
        "onion_store": "🧅 வெங்காயத்தை நன்கு உலர்த்தி உலர்ந்த, காற்றோட்டமான இடத்தில் வைக்கவும்.",
        "onion_humidity": "💧 அதிக ஈரப்பதத்தை தவிர்க்கவும்.",
        "fresh_handle": "🥬 புதிய விளைபொருட்களை மெதுவாக கையாளவும்.",
        "fresh_pack": "📦 காற்றோட்டமான பேக்கேஜிங் பயன்படுத்தவும்.",
        "storage_hot": "☀️ சேமிப்பு வெப்பநிலை அதிகம். பயிரை குளிர்ந்த இடத்திற்கு மாற்றவும்.",
        "storage_cold": "❄️ சேமிப்பு வெப்பநிலை மிகவும் குறைவு.",
        "storage_temp_monitor": "🌡️ சேமிப்பு வெப்பநிலையை தொடர்ந்து கண்காணிக்கவும்.",
        "storage_humidity_high": "💧 சேமிப்பு ஈரப்பதம் அதிகம். காற்றோட்டத்தை மேம்படுத்தவும்.",
        "storage_humidity_low": "🏜️ சேமிப்பு ஈரப்பதம் குறைவு. விளைபொருளை கண்காணிக்கவும்.",
        "storage_humidity_moderate": "💧 சேமிப்பு ஈரப்பதம் மிதமானது.",
        "long_storage": "📅 நீண்டகால சேமிப்பு. தரம் மற்றும் பூச்சிகளை தொடர்ந்து சரிபார்க்கவும்.",
        "medium_storage": "📅 நடுத்தர கால சேமிப்பு. தொடர்ந்து சரிபார்க்கவும்.",
        "short_storage": "📅 குறுகிய கால சேமிப்பு. சுத்தமாகவும் பாதுகாப்பாகவும் வைக்கவும்.",
        "storage_crop_search": "{crop} க்கான தேடல். பயிரை ஏற்றுக்கொள்கிறார்களா என்பதை உறுதிசெய்யவும்.",
        "address_unavailable": "முகவரி கிடைக்கவில்லை",
        "contact_unavailable": "பொதுவாக கிடைக்கவில்லை",
        "confirm_contact": "உறுதிப்படுத்த தொடர்பு கொள்ளவும்",
        "available": "கிடைக்கிறது",
        "check_availability": "கிடைப்பதை சரிபார்க்கவும்",
        "market_config": "அரசு மண்டி API இன்னும் அமைக்கப்படவில்லை. போலி விலை காட்டப்படவில்லை.",
        "market_no_data": "தேர்ந்தெடுக்கப்பட்ட பயிருக்கு நம்பகமான மண்டி விலை கிடைக்கவில்லை.",
        "market_data_found": "{level} நிலையில் மண்டி தகவல் கிடைத்தது.",
        "market_best": "சிறந்த சந்தை: {market}. மாடல் விலை: {price}.",
        "market_area_note": " '{city}' க்கு exact area filter பயன்படுத்தப்படவில்லை.",
        "market_load_failed": "சந்தை தகவலை ஏற்ற முடியவில்லை.",
        "visual_note": "காட்சி பகுப்பாய்வு மட்டும்."
    },


    "te": {
        "unknown": "తెలియదు",
        "not_available": "అందుబాటులో లేదు",
        "storage_facility": "నిల్వ సౌకర్యం",
        "high_humidity": "🌧️ తేమ ఎక్కువగా ఉంది. పంటల్లో ఫంగస్ సమస్యలను గమనించండి.",
        "low_humidity": "💧 తేమ తక్కువగా ఉంది. నేల తేమను క్రమం తప్పకుండా తనిఖీ చేయండి.",
        "moderate_humidity": "🌱 తేమ మితమైన స్థాయిలో ఉంది.",
        "high_temperature": "☀️ ఉష్ణోగ్రత ఎక్కువగా ఉంది. తగినంత నీటిపారుదల చేయండి.",
        "low_temperature": "❄️ ఉష్ణోగ్రత తక్కువగా ఉంది. సున్నితమైన పంటలను రక్షించండి.",
        "suitable_temperature": "🌤️ ఉష్ణోగ్రత అనేక పంటలకు అనుకూలంగా ఉంది.",
        "strong_wind": "💨 గాలి వేగం ఎక్కువగా ఉంది. మొక్కలను తనిఖీ చేయండి.",
        "irrigation_recommended": "💧 నీటిపారుదల సిఫార్సు",
        "moderate_moisture": "🌿 నేల తేమ మితంగా ఉంది",
        "irrigation_not_needed": "✅ వెంటనే నీటిపారుదల అవసరం లేదు",
        "low_soil_moisture": "🌱 నేల తేమ తక్కువగా ఉంది. నీటిపారుదల అవసరం కావచ్చు.",
        "moderate_soil_moisture": "🌿 నేల తేమ మితంగా ఉంది. నీటిపారుదల ముందు నేలను తనిఖీ చేయండి.",
        "high_soil_moisture": "💧 నేల తేమ ఎక్కువగా ఉంది. అనవసర నీటిపారుదలను నివారించండి.",
        "hot_irrigation": "☀️ ఉష్ణోగ్రత ఎక్కువ. నేల తేమను తరచుగా తనిఖీ చేయండి.",
        "cold_irrigation": "❄️ ఉష్ణోగ్రత తక్కువ. అనవసరంగా నీరు ఇవ్వవద్దు.",
        "moderate_temperature": "🌤️ ఉష్ణోగ్రత మితంగా ఉంది.",
        "high_irrigation_humidity": "🌧️ తేమ ఎక్కువ. అధిక నీటిపారుదలను నివారించండి.",
        "low_irrigation_humidity": "💨 తేమ తక్కువ. మొక్కలు వేగంగా నీటిని కోల్పోవచ్చు.",
        "moderate_irrigation_humidity": "💧 తేమ మితంగా ఉంది.",
        "heavy_rain": "🌧️ గణనీయమైన వర్షపాతం ఉంది. నేల తడిగా ఉంటే నీటిపారుదల తగ్గించండి.",
        "some_rain": "🌦️ కొంత వర్షపాతం ఉంది. నీరు ఇవ్వడానికి ముందు నేల తేమను తనిఖీ చేయండి.",
        "no_rain": "☀️ గణనీయమైన వర్షపాతం లేదు. నేల తేమను గమనించండి.",
        "sort_storage": "🧺 నిల్వకు ముందు దెబ్బతిన్న పంటలను వేరు చేయండి.",
        "clean_storage": "🧼 నిల్వ ప్రదేశం మరియు పరికరాలను శుభ్రంగా, పొడిగా ఉంచండి.",
        "air_storage": "📦 కంటైనర్లను అధికంగా నింపవద్దు. సరైన గాలి ప్రసరణ ఉండాలి.",
        "grain_dry": "🌾 దీర్ఘకాల నిల్వకు ముందు ధాన్యాలను బాగా ఆరబెట్టండి.",
        "grain_protect": "💧 ధాన్యాలను తేమ, పురుగులు మరియు ఎలుకల నుండి రక్షించండి.",
        "potato_store": "🥔 బంగాళాదుంపలను చల్లని, చీకటి మరియు గాలి ప్రసరణ ఉన్న ప్రదేశంలో ఉంచండి.",
        "potato_sun": "☀️ బంగాళాదుంపలను నేరుగా సూర్యకాంతి నుండి దూరంగా ఉంచండి.",
        "onion_store": "🧅 ఉల్లిపాయలను బాగా ఆరబెట్టి పొడి, గాలి ప్రసరణ ఉన్న ప్రదేశంలో ఉంచండి.",
        "onion_humidity": "💧 అధిక తేమను నివారించండి.",
        "fresh_handle": "🥬 తాజా పంటలను జాగ్రత్తగా నిర్వహించండి.",
        "fresh_pack": "📦 సరైన గాలి ప్రసరణ ఉన్న ప్యాకేజింగ్ ఉపయోగించండి.",
        "storage_hot": "☀️ నిల్వ ఉష్ణోగ్రత చాలా ఎక్కువ. పంటను చల్లని ప్రదేశానికి మార్చండి.",
        "storage_cold": "❄️ నిల్వ ఉష్ణోగ్రత చాలా తక్కువ.",
        "storage_temp_monitor": "🌡️ నిల్వ ఉష్ణోగ్రతను క్రమం తప్పకుండా గమనించండి.",
        "storage_humidity_high": "💧 నిల్వ తేమ ఎక్కువ. గాలి ప్రసరణను మెరుగుపరచండి.",
        "storage_humidity_low": "🏜️ నిల్వ తేమ తక్కువ. పంటను గమనించండి.",
        "storage_humidity_moderate": "💧 నిల్వ తేమ మితంగా ఉంది.",
        "long_storage": "📅 దీర్ఘకాల నిల్వ. నాణ్యత మరియు పురుగులను క్రమం తప్పకుండా తనిఖీ చేయండి.",
        "medium_storage": "📅 మధ్యకాల నిల్వ. క్రమం తప్పకుండా తనిఖీ చేయండి.",
        "short_storage": "📅 స్వల్పకాల నిల్వ. శుభ్రంగా మరియు సురక్షితంగా ఉంచండి.",
        "storage_crop_search": "{crop} కోసం శోధన. పంటను అంగీకరిస్తారో లేదో నిర్ధారించండి.",
        "address_unavailable": "చిరునామా అందుబాటులో లేదు",
        "contact_unavailable": "ప్రజలకు అందుబాటులో లేదు",
        "confirm_contact": "నిర్ధారించడానికి సౌకర్యాన్ని సంప్రదించండి",
        "available": "అందుబాటులో ఉంది",
        "check_availability": "లభ్యతను తనిఖీ చేయండి",
        "market_config": "ప్రభుత్వ మండి API ఇంకా కాన్ఫిగర్ కాలేదు. నకిలీ ధర చూపించలేదు.",
        "market_no_data": "ఎంచుకున్న పంటకు నమ్మదగిన మండి ధర దొరకలేదు.",
        "market_data_found": "{level} స్థాయిలో మండి సమాచారం లభించింది.",
        "market_best": "ఉత్తమ మార్కెట్: {market}. మోడల్ ధర: {price}.",
        "market_area_note": " '{city}' కోసం exact area filter ఉపయోగించలేదు.",
        "market_load_failed": "మార్కెట్ డేటా లోడ్ కాలేదు.",
        "visual_note": "దృశ్య విశ్లేషణ మాత్రమే."
    },


    "mr": {
        "unknown": "अज्ञात",
        "not_available": "उपलब्ध नाही",
        "storage_facility": "साठवण सुविधा",
        "high_humidity": "🌧️ आर्द्रता जास्त आहे. पिकांमध्ये बुरशीजन्य समस्या तपासा.",
        "low_humidity": "💧 आर्द्रता कमी आहे. मातीतील ओलावा तपासा.",
        "moderate_humidity": "🌱 आर्द्रता मध्यम आहे.",
        "high_temperature": "☀️ तापमान जास्त आहे. पुरेसे सिंचन करा.",
        "low_temperature": "❄️ तापमान कमी आहे. संवेदनशील पिकांचे संरक्षण करा.",
        "suitable_temperature": "🌤️ तापमान अनेक पिकांसाठी योग्य आहे.",
        "strong_wind": "💨 वाऱ्याचा वेग जास्त आहे. पिकांची तपासणी करा.",
        "irrigation_recommended": "💧 सिंचनाची शिफारस",
        "moderate_moisture": "🌿 मातीतील ओलावा मध्यम",
        "irrigation_not_needed": "✅ त्वरित सिंचनाची गरज नाही",
        "low_soil_moisture": "🌱 मातीतील ओलावा कमी आहे. सिंचनाची गरज असू शकते.",
        "moderate_soil_moisture": "🌿 मातीतील ओलावा मध्यम आहे.",
        "high_soil_moisture": "💧 मातीतील ओलावा जास्त आहे. अनावश्यक सिंचन टाळा.",
        "hot_irrigation": "☀️ तापमान जास्त आहे. मातीतील ओलावा वारंवार तपासा.",
        "cold_irrigation": "❄️ तापमान कमी आहे. अनावश्यक पाणी देणे टाळा.",
        "moderate_temperature": "🌤️ तापमान मध्यम आहे.",
        "high_irrigation_humidity": "🌧️ आर्द्रता जास्त आहे. जास्त सिंचन टाळा.",
        "low_irrigation_humidity": "💨 आर्द्रता कमी आहे. पिके लवकर पाणी गमावू शकतात.",
        "moderate_irrigation_humidity": "💧 आर्द्रता मध्यम आहे.",
        "heavy_rain": "🌧️ लक्षणीय पाऊस झाला आहे. माती ओली असल्यास सिंचन कमी करा.",
        "some_rain": "🌦️ काही पाऊस झाला आहे. पाणी देण्यापूर्वी माती तपासा.",
        "no_rain": "☀️ लक्षणीय पाऊस नाही. मातीतील ओलावा तपासा.",
        "sort_storage": "🧺 साठवणीपूर्वी खराब किंवा रोगग्रस्त पिके वेगळी करा.",
        "clean_storage": "🧼 साठवण जागा आणि साधने स्वच्छ व कोरडी ठेवा.",
        "air_storage": "📦 कंटेनर जास्त भरू नका आणि योग्य हवा खेळती ठेवा.",
        "grain_dry": "🌾 दीर्घकालीन साठवणीपूर्वी धान्य व्यवस्थित वाळवा.",
        "grain_protect": "💧 धान्याला ओलावा, कीटक आणि उंदरांपासून वाचवा.",
        "potato_store": "🥔 बटाटे थंड, अंधाऱ्या आणि हवेशीर ठिकाणी ठेवा.",
        "potato_sun": "☀️ बटाटे थेट सूर्यप्रकाशापासून दूर ठेवा.",
        "onion_store": "🧅 कांदे व्यवस्थित वाळवून कोरड्या, हवेशीर ठिकाणी ठेवा.",
        "onion_humidity": "💧 जास्त आर्द्रता टाळा.",
        "fresh_handle": "🥬 ताज्या पिकांना काळजीपूर्वक हाताळा.",
        "fresh_pack": "📦 योग्य हवेशीर पॅकेजिंग वापरा.",
        "storage_hot": "☀️ साठवण तापमान खूप जास्त आहे. पिके थंड ठिकाणी हलवा.",
        "storage_cold": "❄️ साठवण तापमान खूप कमी आहे.",
        "storage_temp_monitor": "🌡️ साठवण तापमान नियमित तपासा.",
        "storage_humidity_high": "💧 साठवण आर्द्रता जास्त आहे. हवा खेळती ठेवा.",
        "storage_humidity_low": "🏜️ साठवण आर्द्रता कमी आहे. पिकांचे निरीक्षण करा.",
        "storage_humidity_moderate": "💧 साठवण आर्द्रता मध्यम आहे.",
        "long_storage": "📅 दीर्घकालीन साठवण. गुणवत्ता आणि कीटकांची नियमित तपासणी करा.",
        "medium_storage": "📅 मध्यम कालावधीची साठवण. नियमित तपासणी करा.",
        "short_storage": "📅 अल्पकालीन साठवण. पिके स्वच्छ आणि सुरक्षित ठेवा.",
        "storage_crop_search": "{crop} साठी शोध घेण्यात आला. सुविधा पिक स्वीकारते का ते तपासा.",
        "address_unavailable": "पत्ता उपलब्ध नाही",
        "contact_unavailable": "सार्वजनिकरीत्या उपलब्ध नाही",
        "confirm_contact": "पुष्टीसाठी सुविधेशी संपर्क करा",
        "available": "उपलब्ध",
        "check_availability": "उपलब्धता तपासा",
        "market_config": "सरकारी मंडी API अजून कॉन्फिगर केलेले नाही. बनावट किंमत दाखवलेली नाही.",
        "market_no_data": "निवडलेल्या पिकासाठी विश्वसनीय मंडी किंमत मिळाली नाही.",
        "market_data_found": "{level} स्तरावर मंडी माहिती मिळाली.",
        "market_best": "सर्वोत्तम बाजार: {market}. मॉडेल किंमत: {price}.",
        "market_area_note": " '{city}' साठी exact area filter वापरलेले नाही.",
        "market_load_failed": "बाजार माहिती लोड होऊ शकली नाही.",
        "visual_note": "फक्त दृश्य विश्लेषण."
    },


    "gu": {
        "unknown": "અજ્ઞાત",
        "not_available": "ઉપલબ્ધ નથી",
        "storage_facility": "સંગ્રહ સુવિધા",
        "high_humidity": "🌧️ ભેજ વધારે છે. પાકમાં ફૂગની સમસ્યાઓ પર ધ્યાન આપો.",
        "low_humidity": "💧 ભેજ ઓછો છે. જમીનની ભેજ તપાસો.",
        "moderate_humidity": "🌱 ભેજ મધ્યમ સ્તરે છે.",
        "high_temperature": "☀️ તાપમાન વધારે છે. પૂરતું સિંચાઈ કરો.",
        "low_temperature": "❄️ તાપમાન ઓછું છે. સંવેદનશીલ પાકનું રક્ષણ કરો.",
        "suitable_temperature": "🌤️ તાપમાન ઘણા પાક માટે યોગ્ય છે.",
        "strong_wind": "💨 પવનની ગતિ વધારે છે. છોડ તપાસો.",
        "irrigation_recommended": "💧 સિંચાઈની ભલામણ",
        "moderate_moisture": "🌿 જમીનની ભેજ મધ્યમ છે",
        "irrigation_not_needed": "✅ તાત્કાલિક સિંચાઈની જરૂર નથી",
        "low_soil_moisture": "🌱 જમીનની ભેજ ઓછી છે. સિંચાઈ જરૂરી હોઈ શકે છે.",
        "moderate_soil_moisture": "🌿 જમીનની ભેજ મધ્યમ છે.",
        "high_soil_moisture": "💧 જમીનની ભેજ વધારે છે. બિનજરૂરી સિંચાઈ ટાળો.",
        "hot_irrigation": "☀️ તાપમાન વધારે છે. જમીનની ભેજ વારંવાર તપાસો.",
        "cold_irrigation": "❄️ તાપમાન ઓછું છે. બિનજરૂરી પાણી આપવાનું ટાળો.",
        "moderate_temperature": "🌤️ તાપમાન મધ્યમ છે.",
        "high_irrigation_humidity": "🌧️ ભેજ વધારે છે. વધારે સિંચાઈ ટાળો.",
        "low_irrigation_humidity": "💨 ભેજ ઓછી છે. છોડ ઝડપથી પાણી ગુમાવી શકે છે.",
        "moderate_irrigation_humidity": "💧 ભેજ મધ્યમ છે.",
        "heavy_rain": "🌧️ નોંધપાત્ર વરસાદ થયો છે. જમીન ભીની હોય તો સિંચાઈ ઘટાડો.",
        "some_rain": "🌦️ થોડો વરસાદ થયો છે. પાણી આપતા પહેલા જમીનની ભેજ તપાસો.",
        "no_rain": "☀️ નોંધપાત્ર વરસાદ નથી. જમીનની ભેજ તપાસતા રહો.",
        "sort_storage": "🧺 સંગ્રહ પહેલાં નુકસાનગ્રસ્ત પાક અલગ કરો.",
        "clean_storage": "🧼 સંગ્રહ વિસ્તાર અને સાધનો સ્વચ્છ અને સૂકા રાખો.",
        "air_storage": "📦 કન્ટેનર વધારે ન ભરો અને યોગ્ય હવા પ્રવાહ રાખો.",
        "grain_dry": "🌾 લાંબા સમયના સંગ્રહ પહેલાં અનાજ સારી રીતે સૂકવો.",
        "grain_protect": "💧 અનાજને ભેજ, જીવાત અને ઉંદરથી બચાવો.",
        "potato_store": "🥔 બટાકા ઠંડી, અંધારી અને હવાદાર જગ્યાએ રાખો.",
        "potato_sun": "☀️ બટાકાને સીધા સૂર્યપ્રકાશથી દૂર રાખો.",
        "onion_store": "🧅 ડુંગળીને સારી રીતે સૂકવીને સૂકી અને હવાદાર જગ્યાએ રાખો.",
        "onion_humidity": "💧 વધારે ભેજ ટાળો.",
        "fresh_handle": "🥬 તાજા પાકને કાળજીપૂર્વક હેન્ડલ કરો.",
        "fresh_pack": "📦 યોગ્ય હવાદાર પેકેજિંગ વાપરો.",
        "storage_hot": "☀️ સંગ્રહનું તાપમાન ખૂબ વધારે છે. પાકને ઠંડી જગ્યાએ ખસેડો.",
        "storage_cold": "❄️ સંગ્રહનું તાપમાન ખૂબ ઓછું છે.",
        "storage_temp_monitor": "🌡️ સંગ્રહનું તાપમાન નિયમિત તપાસો.",
        "storage_humidity_high": "💧 સંગ્રહમાં ભેજ વધારે છે. હવા પ્રવાહ સુધારો.",
        "storage_humidity_low": "🏜️ સંગ્રહમાં ભેજ ઓછી છે. પાકનું નિરીક્ષણ કરો.",
        "storage_humidity_moderate": "💧 સંગ્રહની ભેજ મધ્યમ છે.",
        "long_storage": "📅 લાંબા સમયનો સંગ્રહ. ગુણવત્તા અને જીવાત તપાસો.",
        "medium_storage": "📅 મધ્યમ સમયનો સંગ્રહ. નિયમિત તપાસ કરો.",
        "short_storage": "📅 ટૂંકા સમયનો સંગ્રહ. પાક સ્વચ્છ અને સુરક્ષિત રાખો.",
        "storage_crop_search": "{crop} માટે શોધ કરવામાં આવી છે. સુવિધા પાક સ્વીકારે છે કે નહીં તે તપાસો.",
        "address_unavailable": "સરનામું ઉપલબ્ધ નથી",
        "contact_unavailable": "જાહેર રીતે ઉપલબ્ધ નથી",
        "confirm_contact": "પુષ્ટિ માટે સુવિધાનો સંપર્ક કરો",
        "available": "ઉપલબ્ધ",
        "check_availability": "ઉપલબ્ધતા તપાસો",
        "market_config": "સરકારી મંડી API હજુ કન્ફિગર થયેલ નથી. નકલી કિંમત બતાવવામાં આવી નથી.",
        "market_no_data": "પસંદ કરેલા પાક માટે વિશ્વસનીય મંડી કિંમત મળી નથી.",
        "market_data_found": "{level} સ્તરે મંડી માહિતી મળી.",
        "market_best": "શ્રેષ્ઠ બજાર: {market}. મોડલ કિંમત: {price}.",
        "market_area_note": " '{city}' માટે exact area filter વપરાયું નથી.",
        "market_load_failed": "બજાર માહિતી લોડ થઈ શકી નથી.",
        "visual_note": "માત્ર દૃશ્ય વિશ્લેષણ."
    },


    "kn": {
        "unknown": "ತಿಳಿದಿಲ್ಲ",
        "not_available": "ಲಭ್ಯವಿಲ್ಲ",
        "storage_facility": "ಸಂಗ್ರಹಣಾ ಸೌಲಭ್ಯ",
        "high_humidity": "🌧️ ತೇವಾಂಶ ಹೆಚ್ಚಾಗಿದೆ. ಬೆಳೆಗಳಲ್ಲಿ ಶಿಲೀಂಧ್ರ ಸಮಸ್ಯೆ ಗಮನಿಸಿ.",
        "low_humidity": "💧 ತೇವಾಂಶ ಕಡಿಮೆಯಾಗಿದೆ. ಮಣ್ಣಿನ ತೇವಾಂಶ ಪರಿಶೀಲಿಸಿ.",
        "moderate_humidity": "🌱 ತೇವಾಂಶ ಮಧ್ಯಮ ಮಟ್ಟದಲ್ಲಿದೆ.",
        "high_temperature": "☀️ ತಾಪಮಾನ ಹೆಚ್ಚಾಗಿದೆ. ಸಾಕಷ್ಟು ನೀರಾವರಿ ಮಾಡಿ.",
        "low_temperature": "❄️ ತಾಪಮಾನ ಕಡಿಮೆಯಾಗಿದೆ. ಸೂಕ್ಷ್ಮ ಬೆಳೆಗಳನ್ನು ರಕ್ಷಿಸಿ.",
        "suitable_temperature": "🌤️ ತಾಪಮಾನ ಅನೇಕ ಬೆಳೆಗಳಿಗೆ ಸೂಕ್ತವಾಗಿದೆ.",
        "strong_wind": "💨 ಗಾಳಿಯ ವೇಗ ಹೆಚ್ಚಾಗಿದೆ. ಸಸ್ಯಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.",
        "irrigation_recommended": "💧 ನೀರಾವರಿ ಶಿಫಾರಸು",
        "moderate_moisture": "🌿 ಮಣ್ಣಿನ ತೇವಾಂಶ ಮಧ್ಯಮವಾಗಿದೆ",
        "irrigation_not_needed": "✅ ತಕ್ಷಣ ನೀರಾವರಿ ಅಗತ್ಯವಿಲ್ಲ",
        "low_soil_moisture": "🌱 ಮಣ್ಣಿನ ತೇವಾಂಶ ಕಡಿಮೆಯಾಗಿದೆ. ನೀರಾವರಿ ಬೇಕಾಗಬಹುದು.",
        "moderate_soil_moisture": "🌿 ಮಣ್ಣಿನ ತೇವಾಂಶ ಮಧ್ಯಮವಾಗಿದೆ.",
        "high_soil_moisture": "💧 ಮಣ್ಣಿನ ತೇವಾಂಶ ಹೆಚ್ಚಾಗಿದೆ. ಅನಗತ್ಯ ನೀರಾವರಿ ತಪ್ಪಿಸಿ.",
        "hot_irrigation": "☀️ ತಾಪಮಾನ ಹೆಚ್ಚಾಗಿದೆ. ಮಣ್ಣಿನ ತೇವಾಂಶವನ್ನು ಹೆಚ್ಚು ಬಾರಿ ಪರಿಶೀಲಿಸಿ.",
        "cold_irrigation": "❄️ ತಾಪಮಾನ ಕಡಿಮೆಯಾಗಿದೆ. ಅನಗತ್ಯ ನೀರು ನೀಡುವುದನ್ನು ತಪ್ಪಿಸಿ.",
        "moderate_temperature": "🌤️ ತಾಪಮಾನ ಮಧ್ಯಮವಾಗಿದೆ.",
        "high_irrigation_humidity": "🌧️ ತೇವಾಂಶ ಹೆಚ್ಚಾಗಿದೆ. ಹೆಚ್ಚು ನೀರಾವರಿ ತಪ್ಪಿಸಿ.",
        "low_irrigation_humidity": "💨 ತೇವಾಂಶ ಕಡಿಮೆಯಾಗಿದೆ. ಸಸ್ಯಗಳು ವೇಗವಾಗಿ ನೀರು ಕಳೆದುಕೊಳ್ಳಬಹುದು.",
        "moderate_irrigation_humidity": "💧 ತೇವಾಂಶ ಮಧ್ಯಮವಾಗಿದೆ.",
        "heavy_rain": "🌧️ ಗಮನಾರ್ಹ ಮಳೆಯಾಗಿದೆ. ಮಣ್ಣು ತೇವವಾಗಿದ್ದರೆ ನೀರಾವರಿ ಕಡಿಮೆ ಮಾಡಿ.",
        "some_rain": "🌦️ ಸ್ವಲ್ಪ ಮಳೆಯಾಗಿದೆ. ನೀರು ನೀಡುವ ಮೊದಲು ಮಣ್ಣಿನ ತೇವಾಂಶ ಪರಿಶೀಲಿಸಿ.",
        "no_rain": "☀️ ಗಮನಾರ್ಹ ಮಳೆಯಿಲ್ಲ. ಮಣ್ಣಿನ ತೇವಾಂಶ ಗಮನಿಸಿ.",
        "sort_storage": "🧺 ಸಂಗ್ರಹಿಸುವ ಮೊದಲು ಹಾನಿಗೊಳಗಾದ ಬೆಳೆಗಳನ್ನು ಬೇರ್ಪಡಿಸಿ.",
        "clean_storage": "🧼 ಸಂಗ್ರಹಣಾ ಸ್ಥಳ ಮತ್ತು ಉಪಕರಣಗಳನ್ನು ಸ್ವಚ್ಛವಾಗಿ ಮತ್ತು ಒಣವಾಗಿಡಿ.",
        "air_storage": "📦 ಪಾತ್ರೆಗಳನ್ನು ಹೆಚ್ಚು ತುಂಬಬೇಡಿ ಮತ್ತು ಸರಿಯಾದ ಗಾಳಿಯ ಹರಿವು ಇರಲಿ.",
        "grain_dry": "🌾 ದೀರ್ಘಕಾಲ ಸಂಗ್ರಹಿಸುವ ಮೊದಲು ಧಾನ್ಯಗಳನ್ನು ಚೆನ್ನಾಗಿ ಒಣಗಿಸಿ.",
        "grain_protect": "💧 ಧಾನ್ಯಗಳನ್ನು ತೇವಾಂಶ, ಕೀಟಗಳು ಮತ್ತು ಇಲಿಗಳಿಂದ ರಕ್ಷಿಸಿ.",
        "potato_store": "🥔 ಆಲೂಗಡ್ಡೆಯನ್ನು ತಂಪಾದ, ಕತ್ತಲೆಯ ಮತ್ತು ಗಾಳಿಯಾಡುವ ಸ್ಥಳದಲ್ಲಿ ಇಡಿ.",
        "potato_sun": "☀️ ಆಲೂಗಡ್ಡೆಯನ್ನು ನೇರ ಸೂರ್ಯನ ಬೆಳಕಿನಿಂದ ದೂರವಿಡಿ.",
        "onion_store": "🧅 ಈರುಳ್ಳಿಯನ್ನು ಚೆನ್ನಾಗಿ ಒಣಗಿಸಿ ಒಣ ಮತ್ತು ಗಾಳಿಯಾಡುವ ಸ್ಥಳದಲ್ಲಿ ಇಡಿ.",
        "onion_humidity": "💧 ಹೆಚ್ಚಿನ ತೇವಾಂಶ ತಪ್ಪಿಸಿ.",
        "fresh_handle": "🥬 ತಾಜಾ ಬೆಳೆಗಳನ್ನು ಎಚ್ಚರಿಕೆಯಿಂದ ನಿರ್ವಹಿಸಿ.",
        "fresh_pack": "📦 ಸೂಕ್ತ ಗಾಳಿಯಾಡುವ ಪ್ಯಾಕೇಜಿಂಗ್ ಬಳಸಿ.",
        "storage_hot": "☀️ ಸಂಗ್ರಹಣಾ ತಾಪಮಾನ ತುಂಬಾ ಹೆಚ್ಚಾಗಿದೆ. ಬೆಳೆಗಳನ್ನು ತಂಪಾದ ಸ್ಥಳಕ್ಕೆ ಸರಿಸಿ.",
        "storage_cold": "❄️ ಸಂಗ್ರಹಣಾ ತಾಪಮಾನ ತುಂಬಾ ಕಡಿಮೆಯಾಗಿದೆ.",
        "storage_temp_monitor": "🌡️ ಸಂಗ್ರಹಣಾ ತಾಪಮಾನವನ್ನು ನಿಯಮಿತವಾಗಿ ಪರಿಶೀಲಿಸಿ.",
        "storage_humidity_high": "💧 ಸಂಗ್ರಹಣೆಯಲ್ಲಿ ತೇವಾಂಶ ಹೆಚ್ಚಾಗಿದೆ. ಗಾಳಿಯ ಹರಿವು ಸುಧಾರಿಸಿ.",
        "storage_humidity_low": "🏜️ ಸಂಗ್ರಹಣೆಯ ತೇವಾಂಶ ಕಡಿಮೆಯಾಗಿದೆ. ಬೆಳೆ ಗಮನಿಸಿ.",
        "storage_humidity_moderate": "💧 ಸಂಗ್ರಹಣೆಯ ತೇವಾಂಶ ಮಧ್ಯಮವಾಗಿದೆ.",
        "long_storage": "📅 ದೀರ್ಘಕಾಲದ ಸಂಗ್ರಹಣೆ. ಗುಣಮಟ್ಟ ಮತ್ತು ಕೀಟಗಳನ್ನು ನಿಯಮಿತವಾಗಿ ಪರಿಶೀಲಿಸಿ.",
        "medium_storage": "📅 ಮಧ್ಯಮ ಅವಧಿಯ ಸಂಗ್ರಹಣೆ. ನಿಯಮಿತ ಪರಿಶೀಲನೆ ಮಾಡಿ.",
        "short_storage": "📅 ಕಡಿಮೆ ಅವಧಿಯ ಸಂಗ್ರಹಣೆ. ಬೆಳೆಗಳನ್ನು ಸ್ವಚ್ಛ ಮತ್ತು ಸುರಕ್ಷಿತವಾಗಿಡಿ.",
        "storage_crop_search": "{crop} ಗಾಗಿ ಹುಡುಕಲಾಗಿದೆ. ಸೌಲಭ್ಯವು ಬೆಳೆ ಸ್ವೀಕರಿಸುತ್ತದೆಯೇ ಎಂದು ಖಚಿತಪಡಿಸಿ.",
        "address_unavailable": "ವಿಳಾಸ ಲಭ್ಯವಿಲ್ಲ",
        "contact_unavailable": "ಸಾರ್ವಜನಿಕವಾಗಿ ಲಭ್ಯವಿಲ್ಲ",
        "confirm_contact": "ಖಚಿತಪಡಿಸಲು ಸೌಲಭ್ಯವನ್ನು ಸಂಪರ್ಕಿಸಿ",
        "available": "ಲಭ್ಯವಿದೆ",
        "check_availability": "ಲಭ್ಯತೆ ಪರಿಶೀಲಿಸಿ",
        "market_config": "ಸರ್ಕಾರಿ ಮಂಡಿ API ಇನ್ನೂ ಕಾನ್ಫಿಗರ್ ಆಗಿಲ್ಲ. ನಕಲಿ ಬೆಲೆ ತೋರಿಸಲಾಗಿಲ್ಲ.",
        "market_no_data": "ಆಯ್ಕೆ ಮಾಡಿದ ಬೆಳೆಗೆ ವಿಶ್ವಾಸಾರ್ಹ ಮಂಡಿ ಬೆಲೆ ಸಿಗಲಿಲ್ಲ.",
        "market_data_found": "{level} ಮಟ್ಟದಲ್ಲಿ ಮಂಡಿ ಮಾಹಿತಿ ದೊರಕಿದೆ.",
        "market_best": "ಅತ್ಯುತ್ತಮ ಮಾರುಕಟ್ಟೆ: {market}. ಮಾದರಿ ಬೆಲೆ: {price}.",
        "market_area_note": " '{city}' ಗಾಗಿ exact area filter ಬಳಸಲಾಗಿಲ್ಲ.",
        "market_load_failed": "ಮಾರುಕಟ್ಟೆ ಮಾಹಿತಿ ಲೋಡ್ ಆಗಲಿಲ್ಲ.",
        "visual_note": "ದೃಶ್ಯ ವಿಶ್ಲೇಷಣೆ ಮಾತ್ರ."
    },


    "pa": {
        "unknown": "ਅਣਜਾਣ",
        "not_available": "ਉਪਲਬਧ ਨਹੀਂ",
        "storage_facility": "ਸਟੋਰੇਜ ਸਹੂਲਤ",
        "high_humidity": "🌧️ ਨਮੀ ਜ਼ਿਆਦਾ ਹੈ। ਫਸਲ ਵਿੱਚ ਫੰਗਸ ਸਮੱਸਿਆਵਾਂ ਵੱਲ ਧਿਆਨ ਦਿਓ।",
        "low_humidity": "💧 ਨਮੀ ਘੱਟ ਹੈ। ਮਿੱਟੀ ਦੀ ਨਮੀ ਜਾਂਚੋ।",
        "moderate_humidity": "🌱 ਨਮੀ ਦਰਮਿਆਨੀ ਹੈ।",
        "high_temperature": "☀️ ਤਾਪਮਾਨ ਜ਼ਿਆਦਾ ਹੈ। ਕਾਫ਼ੀ ਸਿੰਚਾਈ ਕਰੋ।",
        "low_temperature": "❄️ ਤਾਪਮਾਨ ਘੱਟ ਹੈ। ਸੰਵੇਦਨਸ਼ੀਲ ਫਸਲਾਂ ਦੀ ਰੱਖਿਆ ਕਰੋ।",
        "suitable_temperature": "🌤️ ਤਾਪਮਾਨ ਕਈ ਫਸਲਾਂ ਲਈ ਢੁਕਵਾਂ ਹੈ।",
        "strong_wind": "💨 ਹਵਾ ਦੀ ਗਤੀ ਜ਼ਿਆਦਾ ਹੈ। ਪੌਦਿਆਂ ਦੀ ਜਾਂਚ ਕਰੋ।",
        "irrigation_recommended": "💧 ਸਿੰਚਾਈ ਦੀ ਸਿਫਾਰਸ਼",
        "moderate_moisture": "🌿 ਮਿੱਟੀ ਦੀ ਨਮੀ ਦਰਮਿਆਨੀ ਹੈ",
        "irrigation_not_needed": "✅ ਤੁਰੰਤ ਸਿੰਚਾਈ ਦੀ ਲੋੜ ਨਹੀਂ",
        "low_soil_moisture": "🌱 ਮਿੱਟੀ ਦੀ ਨਮੀ ਘੱਟ ਹੈ। ਸਿੰਚਾਈ ਦੀ ਲੋੜ ਹੋ ਸਕਦੀ ਹੈ।",
        "moderate_soil_moisture": "🌿 ਮਿੱਟੀ ਦੀ ਨਮੀ ਦਰਮਿਆਨੀ ਹੈ।",
        "high_soil_moisture": "💧 ਮਿੱਟੀ ਦੀ ਨਮੀ ਜ਼ਿਆਦਾ ਹੈ। ਬਿਨਾਂ ਲੋੜ ਸਿੰਚਾਈ ਨਾ ਕਰੋ।",
        "hot_irrigation": "☀️ ਤਾਪਮਾਨ ਜ਼ਿਆਦਾ ਹੈ। ਮਿੱਟੀ ਦੀ ਨਮੀ ਵਾਰ-ਵਾਰ ਜਾਂਚੋ।",
        "cold_irrigation": "❄️ ਤਾਪਮਾਨ ਘੱਟ ਹੈ। ਬਿਨਾਂ ਲੋੜ ਪਾਣੀ ਨਾ ਦਿਓ।",
        "moderate_temperature": "🌤️ ਤਾਪਮਾਨ ਦਰਮਿਆਨਾ ਹੈ।",
        "high_irrigation_humidity": "🌧️ ਨਮੀ ਜ਼ਿਆਦਾ ਹੈ। ਜ਼ਿਆਦਾ ਸਿੰਚਾਈ ਤੋਂ ਬਚੋ।",
        "low_irrigation_humidity": "💨 ਨਮੀ ਘੱਟ ਹੈ। ਪੌਦੇ ਤੇਜ਼ੀ ਨਾਲ ਪਾਣੀ ਗੁਆ ਸਕਦੇ ਹਨ।",
        "moderate_irrigation_humidity": "💧 ਨਮੀ ਦਰਮਿਆਨੀ ਹੈ।",
        "heavy_rain": "🌧️ ਕਾਫ਼ੀ ਮੀਂਹ ਪਿਆ ਹੈ। ਮਿੱਟੀ ਗਿੱਲੀ ਹੋਵੇ ਤਾਂ ਸਿੰਚਾਈ ਘਟਾਓ।",
        "some_rain": "🌦️ ਕੁਝ ਮੀਂਹ ਪਿਆ ਹੈ। ਪਾਣੀ ਦੇਣ ਤੋਂ ਪਹਿਲਾਂ ਮਿੱਟੀ ਦੀ ਨਮੀ ਜਾਂਚੋ।",
        "no_rain": "☀️ ਮਹੱਤਵਪੂਰਨ ਮੀਂਹ ਨਹੀਂ ਪਿਆ। ਮਿੱਟੀ ਦੀ ਨਮੀ ਜਾਂਚਦੇ ਰਹੋ।",
        "sort_storage": "🧺 ਸਟੋਰੇਜ ਤੋਂ ਪਹਿਲਾਂ ਖਰਾਬ ਫਸਲ ਨੂੰ ਵੱਖ ਕਰੋ।",
        "clean_storage": "🧼 ਸਟੋਰੇਜ ਦੀ ਜਗ੍ਹਾ ਅਤੇ ਸੰਦ ਸਾਫ਼ ਅਤੇ ਸੁੱਕੇ ਰੱਖੋ।",
        "air_storage": "📦 ਡੱਬਿਆਂ ਨੂੰ ਜ਼ਿਆਦਾ ਨਾ ਭਰੋ ਅਤੇ ਹਵਾ ਦਾ ਵਧੀਆ ਪ੍ਰਵਾਹ ਰੱਖੋ।",
        "grain_dry": "🌾 ਲੰਬੇ ਸਮੇਂ ਦੀ ਸਟੋਰੇਜ ਤੋਂ ਪਹਿਲਾਂ ਅਨਾਜ ਚੰਗੀ ਤਰ੍ਹਾਂ ਸੁਕਾਓ।",
        "grain_protect": "💧 ਅਨਾਜ ਨੂੰ ਨਮੀ, ਕੀੜਿਆਂ ਅਤੇ ਚੂਹਿਆਂ ਤੋਂ ਬਚਾਓ।",
        "potato_store": "🥔 ਆਲੂਆਂ ਨੂੰ ਠੰਢੀ, ਹਨੇਰੀ ਅਤੇ ਹਵਾਦਾਰ ਜਗ੍ਹਾ ਰੱਖੋ।",
        "potato_sun": "☀️ ਆਲੂਆਂ ਨੂੰ ਸਿੱਧੀ ਧੁੱਪ ਤੋਂ ਦੂਰ ਰੱਖੋ।",
        "onion_store": "🧅 ਪਿਆਜ਼ ਨੂੰ ਚੰਗੀ ਤਰ੍ਹਾਂ ਸੁਕਾ ਕੇ ਸੁੱਕੀ ਅਤੇ ਹਵਾਦਾਰ ਜਗ੍ਹਾ ਰੱਖੋ।",
        "onion_humidity": "💧 ਜ਼ਿਆਦਾ ਨਮੀ ਤੋਂ ਬਚੋ।",
        "fresh_handle": "🥬 ਤਾਜ਼ੀ ਫਸਲ ਨੂੰ ਧਿਆਨ ਨਾਲ ਸੰਭਾਲੋ।",
        "fresh_pack": "📦 ਢੁਕਵੀਂ ਹਵਾਦਾਰ ਪੈਕਿੰਗ ਵਰਤੋ।",
        "storage_hot": "☀️ ਸਟੋਰੇਜ ਦਾ ਤਾਪਮਾਨ ਬਹੁਤ ਜ਼ਿਆਦਾ ਹੈ। ਫਸਲ ਨੂੰ ਠੰਢੀ ਜਗ੍ਹਾ ਰੱਖੋ।",
        "storage_cold": "❄️ ਸਟੋਰੇਜ ਦਾ ਤਾਪਮਾਨ ਬਹੁਤ ਘੱਟ ਹੈ।",
        "storage_temp_monitor": "🌡️ ਸਟੋਰੇਜ ਦਾ ਤਾਪਮਾਨ ਨਿਯਮਿਤ ਜਾਂਚੋ।",
        "storage_humidity_high": "💧 ਸਟੋਰੇਜ ਵਿੱਚ ਨਮੀ ਜ਼ਿਆਦਾ ਹੈ। ਹਵਾ ਦਾ ਪ੍ਰਵਾਹ ਸੁਧਾਰੋ।",
        "storage_humidity_low": "🏜️ ਸਟੋਰੇਜ ਵਿੱਚ ਨਮੀ ਘੱਟ ਹੈ। ਫਸਲ ਦੀ ਨਿਗਰਾਨੀ ਕਰੋ।",
        "storage_humidity_moderate": "💧 ਸਟੋਰੇਜ ਦੀ ਨਮੀ ਦਰਮਿਆਨੀ ਹੈ।",
        "long_storage": "📅 ਲੰਬੇ ਸਮੇਂ ਦੀ ਸਟੋਰੇਜ। ਗੁਣਵੱਤਾ ਅਤੇ ਕੀੜਿਆਂ ਦੀ ਜਾਂਚ ਕਰੋ।",
        "medium_storage": "📅 ਦਰਮਿਆਨੇ ਸਮੇਂ ਦੀ ਸਟੋਰੇਜ। ਨਿਯਮਿਤ ਜਾਂਚ ਕਰੋ।",
        "short_storage": "📅 ਥੋੜ੍ਹੇ ਸਮੇਂ ਦੀ ਸਟੋਰੇਜ। ਫਸਲ ਸਾਫ਼ ਅਤੇ ਸੁਰੱਖਿਅਤ ਰੱਖੋ।",
        "storage_crop_search": "{crop} ਲਈ ਖੋਜ ਕੀਤੀ ਗਈ ਹੈ। ਸਹੂਲਤ ਨਾਲ ਫਸਲ ਸਵੀਕਾਰ ਕਰਨ ਦੀ ਪੁਸ਼ਟੀ ਕਰੋ।",
        "address_unavailable": "ਪਤਾ ਉਪਲਬਧ ਨਹੀਂ",
        "contact_unavailable": "ਜਨਤਕ ਤੌਰ 'ਤੇ ਉਪਲਬਧ ਨਹੀਂ",
        "confirm_contact": "ਪੁਸ਼ਟੀ ਲਈ ਸਹੂਲਤ ਨਾਲ ਸੰਪਰਕ ਕਰੋ",
        "available": "ਉਪਲਬਧ",
        "check_availability": "ਉਪਲਬਧਤਾ ਜਾਂਚੋ",
        "market_config": "ਸਰਕਾਰੀ ਮੰਡੀ API ਹਾਲੇ ਕਨਫਿਗਰ ਨਹੀਂ ਹੈ। ਕੋਈ ਨਕਲੀ ਕੀਮਤ ਨਹੀਂ ਦਿਖਾਈ ਗਈ।",
        "market_no_data": "ਚੁਣੀ ਗਈ ਫਸਲ ਲਈ ਭਰੋਸੇਯੋਗ ਮੰਡੀ ਕੀਮਤ ਨਹੀਂ ਮਿਲੀ।",
        "market_data_found": "{level} ਪੱਧਰ 'ਤੇ ਮੰਡੀ ਜਾਣਕਾਰੀ ਮਿਲੀ।",
        "market_best": "ਸਭ ਤੋਂ ਵਧੀਆ ਬਾਜ਼ਾਰ: {market}। ਮਾਡਲ ਕੀਮਤ: {price}।",
        "market_area_note": " '{city}' ਲਈ exact area filter ਨਹੀਂ ਵਰਤਿਆ ਗਿਆ।",
        "market_load_failed": "ਬਾਜ਼ਾਰ ਦੀ ਜਾਣਕਾਰੀ ਲੋਡ ਨਹੀਂ ਹੋ ਸਕੀ।",
        "visual_note": "ਸਿਰਫ਼ ਦ੍ਰਿਸ਼ਟੀਗਤ ਵਿਸ਼ਲੇਸ਼ਣ।"
    }
}


# =====================================================
# LANGUAGE HELPERS
# =====================================================

def get_language():

    language = request.form.get(
        "language",
        "en"
    ).strip().lower()

    if language not in SUPPORTED_LANGUAGES:
        language = "en"

    return language


def t(key, language="en", **kwargs):

    if language not in SUPPORTED_LANGUAGES:
        language = "en"

    text = TEXT.get(
        language,
        TEXT["en"]
    ).get(
        key,
        TEXT["en"].get(
            key,
            key
        )
    )

    try:
        return text.format(**kwargs)
    except Exception:
        return text


# =====================================================
# CROP TRANSLATIONS
# =====================================================

CROP_TRANSLATIONS = {

    "rice": {
        "en": "Rice", "bn": "ধান", "hi": "चावल",
        "ta": "நெல்", "te": "వరి", "mr": "तांदूळ",
        "gu": "ચોખા", "kn": "ಭತ್ತ", "pa": "ਝੋਨਾ"
    },

    "maize": {
        "en": "Maize", "bn": "ভুট্টা", "hi": "मक्का",
        "ta": "மக்காச்சோளம்", "te": "మొక్కజొన్న", "mr": "मका",
        "gu": "મકાઈ", "kn": "ಮೆಕ್ಕೆಜೋಳ", "pa": "ਮੱਕੀ"
    },

    "wheat": {
        "en": "Wheat", "bn": "গম", "hi": "गेहूँ",
        "ta": "கோதுமை", "te": "గోధుమ", "mr": "गहू",
        "gu": "ઘઉં", "kn": "ಗೋಧಿ", "pa": "ਕਣਕ"
    },

    "potato": {
        "en": "Potato", "bn": "আলু", "hi": "आलू",
        "ta": "உருளைக்கிழங்கு", "te": "బంగాళాదుంప",
        "mr": "बटाटा", "gu": "બટાકા", "kn": "ಆಲೂಗಡ್ಡೆ",
        "pa": "ਆਲੂ"
    },

    "tomato": {
        "en": "Tomato", "bn": "টমেটো", "hi": "टमाटर",
        "ta": "தக்காளி", "te": "టమాటా", "mr": "टोमॅटो",
        "gu": "ટામેટા", "kn": "ಟೊಮ್ಯಾಟೊ", "pa": "ਟਮਾਟਰ"
    },

    "onion": {
        "en": "Onion", "bn": "পেঁয়াজ", "hi": "प्याज़",
        "ta": "வெங்காயம்", "te": "ఉల్లిపాయ", "mr": "कांदा",
        "gu": "ડુંગળી", "kn": "ಈರುಳ್ಳಿ", "pa": "ਪਿਆਜ਼"
    },

    "chilli": {
        "en": "Chilli", "bn": "লঙ্কা", "hi": "मिर्च",
        "ta": "மிளகாய்", "te": "మిరపకాయ", "mr": "मिरची",
        "gu": "મરચું", "kn": "ಮೆಣಸಿನಕಾಯಿ", "pa": "ਮਿਰਚ"
    },

    "cucumber": {
        "en": "Cucumber", "bn": "শসা", "hi": "खीरा",
        "ta": "வெள்ளரிக்காய்", "te": "దోసకాయ", "mr": "काकडी",
        "gu": "કાકડી", "kn": "ಸೌತೆಕಾಯಿ", "pa": "ਖੀਰਾ"
    },

    "brinjal": {
        "en": "Brinjal", "bn": "বেগুন", "hi": "बैंगन",
        "ta": "கத்தரிக்காய்", "te": "వంకాయ", "mr": "वांगी",
        "gu": "રીંગણ", "kn": "ಬದನೆಕಾಯಿ", "pa": "ਬੈਂਗਣ"
    },

    "carrot": {
        "en": "Carrot", "bn": "গাজর", "hi": "गाजर",
        "ta": "கேரட்", "te": "క్యారెట్", "mr": "गाजर",
        "gu": "ગાજર", "kn": "ಕ್ಯಾರೆಟ್", "pa": "ਗਾਜਰ"
    },

    "chickpea": {
        "en": "Chickpea", "bn": "ছোলা", "hi": "चना",
        "ta": "கொண்டைக்கடலை", "te": "శనగ", "mr": "हरभरा",
        "gu": "ચણા", "kn": "ಕಡಲೆ", "pa": "ਛੋਲੇ"
    },

    "kidneybeans": {
        "en": "Kidney Beans", "bn": "রাজমা", "hi": "राजमा",
        "ta": "ராஜ்மா", "te": "రాజ్మా", "mr": "राजमा",
        "gu": "રાજમા", "kn": "ರಾಜ್ಮಾ", "pa": "ਰਾਜਮਾ"
    },

    "pigeonpeas": {
        "en": "Pigeon Peas", "bn": "অড়হর ডাল", "hi": "अरहर दाल",
        "ta": "துவரம் பருப்பு", "te": "కందిపప్పు", "mr": "तूर डाळ",
        "gu": "તુવેર દાળ", "kn": "ತೊಗರಿ ಬೇಳೆ", "pa": "ਤੂਰ ਦਾਲ"
    },

    "mothbeans": {
        "en": "Moth Beans", "bn": "মট ডাল", "hi": "मोठ दाल",
        "ta": "மொத் பீன்ஸ்", "te": "మోత్ బీన్స్", "mr": "मटकी",
        "gu": "મોથ બીન્સ", "kn": "ಮೋತ್ ಬೀನ್ಸ್", "pa": "ਮੋਠ ਦਾਲ"
    },

    "mungbean": {
        "en": "Mung Bean", "bn": "মুগ ডাল", "hi": "मूंग",
        "ta": "பாசிப்பயறு", "te": "పెసలు", "mr": "मूग",
        "gu": "મગ", "kn": "ಹೆಸರುಕಾಳು", "pa": "ਮੂੰਗੀ"
    },

    "blackgram": {
        "en": "Black Gram", "bn": "মাষকলাই", "hi": "उड़द",
        "ta": "உளுந்து", "te": "మినుములు", "mr": "उडीद",
        "gu": "અડદ", "kn": "ಉದ್ದು", "pa": "ਉੜਦ"
    },

    "lentil": {
        "en": "Lentil", "bn": "মসুর ডাল", "hi": "मसूर",
        "ta": "மசூர் பருப்பு", "te": "మసూర్ పప్పు", "mr": "मसूर",
        "gu": "મસૂર", "kn": "ಮಸೂರ್ ಬೇಳೆ", "pa": "ਮਸੂਰ"
    },

    "pomegranate": {
        "en": "Pomegranate", "bn": "ডালিম", "hi": "अनार",
        "ta": "மாதுளை", "te": "దానిమ్మ", "mr": "डाळिंब",
        "gu": "દાડમ", "kn": "ದಾಳಿಂಬೆ", "pa": "ਅਨਾਰ"
    },

    "banana": {
        "en": "Banana", "bn": "কলা", "hi": "केला",
        "ta": "வாழைப்பழம்", "te": "అరటి", "mr": "केळी",
        "gu": "કેળું", "kn": "ಬಾಳೆಹಣ್ಣು", "pa": "ਕੇਲਾ"
    },

    "mango": {
        "en": "Mango", "bn": "আম", "hi": "आम",
        "ta": "மாம்பழம்", "te": "మామిడి", "mr": "आंबा",
        "gu": "કેરી", "kn": "ಮಾವು", "pa": "ਅੰਬ"
    },

    "grapes": {
        "en": "Grapes", "bn": "আঙুর", "hi": "अंगूर",
        "ta": "திராட்சை", "te": "ద్రాక్ష", "mr": "द्राक्षे",
        "gu": "દ્રાક્ષ", "kn": "ದ್ರಾಕ್ಷಿ", "pa": "ਅੰਗੂਰ"
    },

    "watermelon": {
        "en": "Watermelon", "bn": "তরমুজ", "hi": "तरबूज",
        "ta": "தர்பூசணி", "te": "పుచ్చకాయ", "mr": "कलिंगड",
        "gu": "તરબૂચ", "kn": "ಕಲ್ಲಂಗಡಿ", "pa": "ਤਰਬੂਜ"
    },

    "muskmelon": {
        "en": "Muskmelon", "bn": "খরমুজ", "hi": "खरबूजा",
        "ta": "முலாம்பழம்", "te": "ఖర్బూజ", "mr": "खरबूज",
        "gu": "શક્કરટેટી", "kn": "ಕರಬೂಜ", "pa": "ਖਰਬੂਜਾ"
    },

    "apple": {
        "en": "Apple", "bn": "আপেল", "hi": "सेब",
        "ta": "ஆப்பிள்", "te": "ఆపిల్", "mr": "सफरचंद",
        "gu": "સફરજન", "kn": "ಸೇಬು", "pa": "ਸੇਬ"
    },

    "orange": {
        "en": "Orange", "bn": "কমলা", "hi": "संतरा",
        "ta": "ஆரஞ்சு", "te": "నారింజ", "mr": "संत्रे",
        "gu": "નારંગી", "kn": "ಕಿತ್ತಳೆ", "pa": "ਸੰਤਰਾ"
    },

    "papaya": {
        "en": "Papaya", "bn": "পেঁপে", "hi": "पपीता",
        "ta": "பப்பாளி", "te": "బొప్పాయి", "mr": "पपई",
        "gu": "પપૈયું", "kn": "ಪಪ್ಪಾಯಿ", "pa": "ਪਪੀਤਾ"
    },

    "coconut": {
        "en": "Coconut", "bn": "নারকেল", "hi": "नारियल",
        "ta": "தேங்காய்", "te": "కొబ్బరి", "mr": "नारळ",
        "gu": "નાળિયેર", "kn": "ತೆಂಗಿನಕಾಯಿ", "pa": "ਨਾਰੀਅਲ"
    },

    "cotton": {
        "en": "Cotton", "bn": "তুলা", "hi": "कपास",
        "ta": "பருத்தி", "te": "పత్తి", "mr": "कापूस",
        "gu": "કપાસ", "kn": "ಹತ್ತಿ", "pa": "ਕਪਾਹ"
    },

    "jute": {
        "en": "Jute", "bn": "পাট", "hi": "जूट",
        "ta": "சணல்", "te": "జూట్", "mr": "ताग",
        "gu": "શણ", "kn": "ಸೆಣಬು", "pa": "ਜੂਟ"
    },

    "coffee": {
        "en": "Coffee", "bn": "কফি", "hi": "कॉफी",
        "ta": "காபி", "te": "కాఫీ", "mr": "कॉफी",
        "gu": "કોફી", "kn": "ಕಾಫಿ", "pa": "ਕੌਫੀ"
    }
}


# =====================================================
# TRANSLATE CROP NAME
# =====================================================

def translate_crop_name(crop, language="en"):

    if not crop:
        return crop

    if language not in SUPPORTED_LANGUAGES:
        language = "en"

    key = (
        str(crop)
        .strip()
        .lower()
        .replace("_", "")
        .replace("-", "")
        .replace(" ", "")
    )

    translation = CROP_TRANSLATIONS.get(
        key,
        {}
    )

    return translation.get(
        language,
        str(crop).strip().capitalize()
    )


# =====================================================
# LOAD SOIL ML MODEL
# =====================================================

with open(
    "data/model/crop_model.pkl",
    "rb"
) as file:

    model = pickle.load(file)


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =====================================================
# SOIL → CROP RECOMMENDATION
# =====================================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    try:

        location = request.form.get(
            "location",
            ""
        ).strip()

        language = get_language()

        ph = float(request.form.get("ph", 0))
        nitrogen = float(request.form.get("nitrogen", 0))
        phosphorus = float(request.form.get("phosphorus", 0))
        potassium = float(request.form.get("potassium", 0))
        moisture = float(request.form.get("moisture", 0))
        temperature = float(request.form.get("temperature", 0))
        humidity = float(request.form.get("humidity", 0))
        rainfall = float(request.form.get("rainfall", 0))

        season = request.form.get(
            "season",
            ""
        )

        input_data = [[
            nitrogen,
            phosphorus,
            potassium,
            temperature,
            humidity,
            ph,
            rainfall
        ]]

        prediction = model.predict(
            input_data
        )

        recommended_crop = str(
            prediction[0]
        ).strip()

        translated_crop = translate_crop_name(
            recommended_crop,
            language
        )

        recommendations = [
            "🌱 " + translated_crop
        ]

        return render_template(
            "result.html",
            location=location,
            ph=ph,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            moisture=moisture,
            temperature=temperature,
            humidity=humidity,
            rainfall=rainfall,
            season=season,
            recommendations=recommendations,
            language=language
        )

    except Exception as e:

        print(
            "SOIL ANALYSIS ERROR:",
            e
        )

        return """
        <h2>⚠️ Soil analysis failed</h2>
        <p>Please check the entered values.</p>
        <br>
        <a href="/">← Go Back</a>
        """


# =====================================================
# CROP PHOTO → AI ANALYSIS
# =====================================================

@app.route(
    "/analyze-image",
    methods=["POST"]
)
def analyze_image():

    image = request.files.get(
        "crop_image"
    )

    language = get_language()

    if image is None or image.filename == "":

        return """
        <h2>⚠️ Please upload a crop image.</h2>
        <a href="/">← Go Back</a>
        """

    try:

        image_bytes = image.read()

        result = analyze_crop_image(
            image_bytes
        )

        raw_crop = result.get(
            "crop_name",
            "Unknown"
        )

        crop_name = translate_crop_name(
            raw_crop,
            language
        )

        quality = result.get(
            "quality",
            t("unknown", language)
        )

        action = result.get(
            "action",
            []
        )

        note = result.get(
            "note",
            t("visual_note", language)
        )

        return render_template(
            "image_result.html",

            crop_name=crop_name,

            confidence=result.get(
                "confidence",
                0
            ),

            freshness=result.get(
                "freshness",
                0
            ),

            defect=result.get(
                "defect",
                0
            ),

            quality=quality,

            spots=result.get(
                "spots",
                0
            ),

            discoloration=result.get(
                "discoloration",
                0
            ),

            action=action,

            note=note,

            language=language
        )

    except Exception as e:

        print(
            "IMAGE ANALYSIS ERROR:",
            e
        )

        return f"""
        <h2>⚠️ Image analysis failed</h2>
        <p>{str(e)}</p>
        <br>
        <a href="/">← Go Back</a>
        """


# =====================================================
# WEATHER
# =====================================================

@app.route(
    "/weather",
    methods=["POST"]
)
def weather():

    location = request.form.get(
        "weather_location",
        ""
    ).strip()

    language = get_language()

    if not location:

        return """
        <h2>⚠️ Please enter a location.</h2>
        <a href="/">← Go Back</a>
        """

    api_key = os.getenv(
        "OPENWEATHER_API_KEY"
    )

    if not api_key:

        return """
        <h2>⚠️ Weather API key not found.</h2>
        <p>Please check OPENWEATHER_API_KEY.</p>
        <a href="/">← Go Back</a>
        """

    try:

        params = urllib.parse.urlencode({
            "q": location,
            "appid": api_key.strip(),
            "units": "metric"
        })

        url = (
            "https://api.openweathermap.org/data/2.5/weather?"
            + params
        )

        weather_request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                "Smart-Krishi-AI-Project/1.0"
            }
        )

        with urllib.request.urlopen(
            weather_request,
            timeout=15
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        city = data.get(
            "name",
            location
        )

        country = data.get(
            "sys",
            {}
        ).get(
            "country",
            ""
        )

        main_data = data.get(
            "main",
            {}
        )

        temperature = main_data.get(
            "temp",
            0
        )

        humidity = main_data.get(
            "humidity",
            0
        )

        pressure = main_data.get(
            "pressure",
            0
        )

        wind_speed = data.get(
            "wind",
            {}
        ).get(
            "speed",
            0
        )

        weather_description = data.get(
            "weather",
            [{}]
        )[0].get(
            "description",
            t("unknown", language)
        )

        advice = []

        if humidity >= 80:
            advice.append(
                t("high_humidity", language)
            )
        elif humidity <= 40:
            advice.append(
                t("low_humidity", language)
            )
        else:
            advice.append(
                t("moderate_humidity", language)
            )

        if temperature >= 35:
            advice.append(
                t("high_temperature", language)
            )
        elif temperature <= 15:
            advice.append(
                t("low_temperature", language)
            )
        else:
            advice.append(
                t("suitable_temperature", language)
            )

        if wind_speed >= 8:
            advice.append(
                t("strong_wind", language)
            )

        if temperature >= 30:

            crop_keys = [
                "rice",
                "maize",
                "chilli",
                "cucumber"
            ]

            suitable_crops = [
                "🌾 " + translate_crop_name(c, language)
                for c in crop_keys
            ]

        elif temperature >= 20:

            crop_keys = [
                "rice",
                "maize",
                "tomato",
                "cucumber",
                "brinjal"
            ]

            suitable_crops = [
                "🌾 " + translate_crop_name(c, language)
                for c in crop_keys
            ]

        else:

            crop_keys = [
                "potato",
                "carrot",
                "wheat",
                "onion"
            ]

            suitable_crops = [
                "🌾 " + translate_crop_name(c, language)
                for c in crop_keys
            ]

        return render_template(
            "result.html",

            show_weather=True,

            location=location,

            weather_city=city,
            weather_country=country,

            weather_temperature=temperature,
            weather_humidity=humidity,
            weather_pressure=pressure,
            weather_wind_speed=wind_speed,

            weather_description=weather_description,

            weather_advice=advice,

            suitable_crops=suitable_crops,

            language=language
        )

    except urllib.error.HTTPError as e:

        print(
            "WEATHER HTTP ERROR:",
            e.code
        )

        if e.code == 401:
            message = "Invalid or inactive Weather API key."
        elif e.code == 404:
            message = "Location not found."
        else:
            message = f"Weather API error: {e.code}"

        return f"""
        <h2>⚠️ Weather Error</h2>
        <p>{message}</p>
        <br>
        <a href="/">← Go Back</a>
        """

    except Exception as e:

        print(
            "WEATHER ERROR:",
            e
        )

        return """
        <h2>⚠️ Weather request failed</h2>
        <p>Please try again with another location.</p>
        <br>
        <a href="/">← Go Back</a>
        """


# =====================================================
# SMART IRRIGATION
# =====================================================

@app.route(
    "/irrigation",
    methods=["POST"]
)
def irrigation():

    language = get_language()

    try:

        moisture = float(
            request.form.get(
                "irrigation_moisture",
                0
            )
        )

        temperature = float(
            request.form.get(
                "irrigation_temperature",
                0
            )
        )

        humidity = float(
            request.form.get(
                "irrigation_humidity",
                0
            )
        )

        rainfall = float(
            request.form.get(
                "irrigation_rainfall",
                0
            )
        )

        advice = []

        if moisture < 30:

            irrigation_status = t(
                "irrigation_recommended",
                language
            )

            advice.append(
                t(
                    "low_soil_moisture",
                    language
                )
            )

        elif moisture < 60:

            irrigation_status = t(
                "moderate_moisture",
                language
            )

            advice.append(
                t(
                    "moderate_soil_moisture",
                    language
                )
            )

        else:

            irrigation_status = t(
                "irrigation_not_needed",
                language
            )

            advice.append(
                t(
                    "high_soil_moisture",
                    language
                )
            )

        if temperature >= 35:

            advice.append(
                t(
                    "hot_irrigation",
                    language
                )
            )

        elif temperature <= 15:

            advice.append(
                t(
                    "cold_irrigation",
                    language
                )
            )

        else:

            advice.append(
                t(
                    "moderate_temperature",
                    language
                )
            )

        if humidity >= 80:

            advice.append(
                t(
                    "high_irrigation_humidity",
                    language
                )
            )

        elif humidity <= 40:

            advice.append(
                t(
                    "low_irrigation_humidity",
                    language
                )
            )

        else:

            advice.append(
                t(
                    "moderate_irrigation_humidity",
                    language
                )
            )

        if rainfall >= 10:

            advice.append(
                t(
                    "heavy_rain",
                    language
                )
            )

        elif rainfall > 0:

            advice.append(
                t(
                    "some_rain",
                    language
                )
            )

        else:

            advice.append(
                t(
                    "no_rain",
                    language
                )
            )

        return render_template(
            "result.html",

            show_irrigation=True,

            irrigation_moisture=moisture,
            irrigation_temperature=temperature,
            irrigation_humidity=humidity,
            irrigation_rainfall=rainfall,

            irrigation_status=irrigation_status,
            irrigation_advice=advice,

            language=language
        )

    except ValueError:

        return """
        <h2>⚠️ Invalid irrigation data</h2>
        <p>Please enter valid numeric values.</p>
        <br>
        <a href="/">← Go Back</a>
        """

    except Exception as e:

        print(
            "IRRIGATION ERROR:",
            e
        )

        return """
        <h2>⚠️ Irrigation advice failed</h2>
        <a href="/">← Go Back</a>
        """


# =====================================================
# POST-HARVEST & STORAGE GUIDANCE
# =====================================================

@app.route(
    "/storage",
    methods=["POST"]
)
def storage():

    language = get_language()

    try:

        crop = request.form.get(
            "storage_crop",
            ""
        ).strip()

        temperature = float(
            request.form.get(
                "storage_temperature",
                0
            )
        )

        humidity = float(
            request.form.get(
                "storage_humidity",
                0
            )
        )

        storage_days = int(
            request.form.get(
                "storage_days",
                1
            )
        )

        if not crop:

            return """
            <h2>⚠️ Please select a crop.</h2>
            <a href="/">← Go Back</a>
            """

        advice = [

            t(
                "sort_storage",
                language
            ),

            t(
                "clean_storage",
                language
            ),

            t(
                "air_storage",
                language
            )

        ]

        crop_lower = crop.lower()

        if crop_lower in [
            "rice",
            "wheat",
            "maize"
        ]:

            advice.append(
                t(
                    "grain_dry",
                    language
                )
            )

            advice.append(
                t(
                    "grain_protect",
                    language
                )
            )

        elif crop_lower == "potato":

            advice.append(
                t(
                    "potato_store",
                    language
                )
            )

            advice.append(
                t(
                    "potato_sun",
                    language
                )
            )

        elif crop_lower == "onion":

            advice.append(
                t(
                    "onion_store",
                    language
                )
            )

            advice.append(
                t(
                    "onion_humidity",
                    language
                )
            )

        elif crop_lower in [
            "tomato",
            "brinjal",
            "chilli",
            "cucumber",
            "carrot"
        ]:

            advice.append(
                t(
                    "fresh_handle",
                    language
                )
            )

            advice.append(
                t(
                    "fresh_pack",
                    language
                )
            )

        if temperature >= 35:

            advice.append(
                t(
                    "storage_hot",
                    language
                )
            )

        elif temperature <= 5:

            advice.append(
                t(
                    "storage_cold",
                    language
                )
            )

        else:

            advice.append(
                t(
                    "storage_temp_monitor",
                    language
                )
            )

        if humidity >= 80:

            advice.append(
                t(
                    "storage_humidity_high",
                    language
                )
            )

        elif humidity <= 40:

            advice.append(
                t(
                    "storage_humidity_low",
                    language
                )
            )

        else:

            advice.append(
                t(
                    "storage_humidity_moderate",
                    language
                )
            )

        if storage_days >= 30:

            advice.append(
                t(
                    "long_storage",
                    language
                )
            )

        elif storage_days >= 7:

            advice.append(
                t(
                    "medium_storage",
                    language
                )
            )

        else:

            advice.append(
                t(
                    "short_storage",
                    language
                )
            )

        return render_template(
            "result.html",

            show_storage=True,

            storage_crop=translate_crop_name(
                crop,
                language
            ),

            storage_temperature=temperature,
            storage_humidity=humidity,
            storage_days=storage_days,

            storage_advice=advice,

            language=language
        )

    except ValueError:

        return """
        <h2>⚠️ Invalid storage data</h2>
        <p>Please enter valid numeric values.</p>
        <br>
        <a href="/">← Go Back</a>
        """

    except Exception as e:

        print(
            "STORAGE ERROR:",
            e
        )

        return """
        <h2>⚠️ Storage guidance failed</h2>
        <a href="/">← Go Back</a>
        """


# =====================================================
# NEARBY STORAGE FINDER
# =====================================================

@app.route(
    "/storage-finder",
    methods=["POST"]
)
def storage_finder():

    language = get_language()

    location = request.form.get(
        "storage_location",
        ""
    ).strip()

    crop = request.form.get(
        "storage_finder_crop",
        ""
    ).strip()

    if not location:

        return """
        <h2>⚠️ Please enter a location.</h2>
        <a href="/">← Go Back</a>
        """

    if not crop:

        return """
        <h2>⚠️ Please select a crop.</h2>
        <a href="/">← Go Back</a>
        """

    display_crop = translate_crop_name(
        crop,
        language
    )

    try:

        geocode_params = urllib.parse.urlencode({

            "q": location,
            "format": "json",
            "limit": 1,
            "countrycodes": "in"

        })

        geocode_url = (
            "https://nominatim.openstreetmap.org/search?"
            + geocode_params
        )

        geocode_request = urllib.request.Request(

            geocode_url,

            headers={
                "User-Agent":
                "Smart-Krishi-AI-Project/1.0"
            }

        )

        with urllib.request.urlopen(
            geocode_request,
            timeout=15
        ) as response:

            geocode_data = json.loads(
                response.read().decode("utf-8")
            )

        if not geocode_data:

            demo_results = create_demo_storage(
                location,
                crop,
                language
            )

            return render_template(
                "result.html",

                show_storage_finder=True,

                storage_finder_location=location,
                storage_finder_crop=display_crop,

                storage_results=demo_results,
                storage_demo=True,

                language=language
            )

        latitude = float(
            geocode_data[0]["lat"]
        )

        longitude = float(
            geocode_data[0]["lon"]
        )

        print(
            "LOCATION FOUND:",
            location,
            latitude,
            longitude
        )

        radius = 30000

        overpass_query = f"""
[out:json][timeout:25];

(
  nwr[
    amenity="cold_storage"
  ](
    around:{radius},{latitude},{longitude}
  );

  nwr[
    building="warehouse"
  ](
    around:{radius},{latitude},{longitude}
  );

  nwr[
    industrial="warehouse"
  ](
    around:{radius},{latitude},{longitude}
  );

  nwr[
    name~"Cold Storage|Coldstore|Cold Store|Warehouse|Godown|হিমঘর|কোল্ড স্টোরেজ",
    i
  ](
    around:{radius},{latitude},{longitude}
  );
);

out center tags;
"""

        overpass_servers = [

            "https://overpass-api.de/api/interpreter",

            "https://overpass.kumi.systems/api/interpreter",

            "https://overpass.private.coffee/api/interpreter"

        ]

        storage_data = None

        for server in overpass_servers:

            try:

                print(
                    "Trying storage server:",
                    server
                )

                request_data = urllib.parse.urlencode({

                    "data": overpass_query

                }).encode("utf-8")

                overpass_request = urllib.request.Request(

                    server,

                    data=request_data,

                    headers={

                        "User-Agent":
                        "Smart-Krishi-AI-Project/1.0",

                        "Content-Type":
                        "application/x-www-form-urlencoded"

                    }

                )

                with urllib.request.urlopen(
                    overpass_request,
                    timeout=35
                ) as response:

                    storage_data = json.loads(
                        response.read().decode("utf-8")
                    )

                print(
                    "Storage server worked:",
                    server
                )

                break

            except Exception as server_error:

                print(
                    "Storage server failed:",
                    server,
                    server_error
                )

                continue

        if storage_data is None:

            demo_results = create_demo_storage(
                location,
                crop,
                language
            )

            return render_template(

                "result.html",

                show_storage_finder=True,

                storage_finder_location=location,
                storage_finder_crop=display_crop,

                storage_results=demo_results,

                storage_demo=True,
                storage_error=True,

                language=language
            )

        elements = storage_data.get(
            "elements",
            []
        )

        storage_results = []

        for item in elements:

            tags = item.get(
                "tags",
                {}
            )

            name = tags.get(
                "name"
            )

            if not name:
                continue

            if (
                "lat" in item
                and
                "lon" in item
            ):

                storage_lat = float(
                    item["lat"]
                )

                storage_lon = float(
                    item["lon"]
                )

            else:

                center = item.get(
                    "center",
                    {}
                )

                if not center:
                    continue

                if (
                    "lat" not in center
                    or
                    "lon" not in center
                ):
                    continue

                storage_lat = float(
                    center["lat"]
                )

                storage_lon = float(
                    center["lon"]
                )

            earth_radius = 6371.0

            lat1 = radians(
                latitude
            )

            lat2 = radians(
                storage_lat
            )

            delta_lat = radians(
                storage_lat - latitude
            )

            delta_lon = radians(
                storage_lon - longitude
            )

            a = (
                sin(delta_lat / 2) ** 2
                +
                cos(lat1)
                *
                cos(lat2)
                *
                sin(delta_lon / 2) ** 2
            )

            c = 2 * atan2(
                sqrt(a),
                sqrt(1 - a)
            )

            distance = (
                earth_radius * c
            )

            address_parts = []

            for key in [

                "addr:housenumber",
                "addr:street",
                "addr:village",
                "addr:town",
                "addr:city",
                "addr:district",
                "addr:state"

            ]:

                value = tags.get(
                    key
                )

                if (
                    value
                    and
                    value not in address_parts
                ):

                    address_parts.append(
                        value
                    )

            address = ", ".join(
                address_parts
            )

            if not address:

                address = t(
                    "address_unavailable",
                    language
                )

            phone = tags.get(
                "contact:phone"
            )

            if not phone:

                phone = tags.get(
                    "phone"
                )

            website = tags.get(
                "contact:website"
            )

            if not website:

                website = tags.get(
                    "website"
                )

            if tags.get("amenity"):

                storage_type = tags.get(
                    "amenity"
                )

            elif tags.get("industrial"):

                storage_type = tags.get(
                    "industrial"
                )

            elif tags.get("building"):

                storage_type = tags.get(
                    "building"
                )

            else:

                storage_type = t(
                    "storage_facility",
                    language
                )

            map_url = (

                "https://www.openstreetmap.org/"

                f"?mlat={storage_lat}"

                f"&mlon={storage_lon}"

                "#map=17/"

                f"{storage_lat}/"

                f"{storage_lon}"

            )

            storage_results.append({

                "name":
                    name,

                "location":
                    address,

                "distance":
                    f"{distance:.1f} km",

                "type":
                    storage_type,

                "crops":
                    t(
                        "storage_crop_search",
                        language,
                        crop=display_crop
                    ),

                "rent":
                    t(
                        "not_available",
                        language
                    ),

                "availability":
                    t(
                        "confirm_contact",
                        language
                    ),

                "contact":
                    (
                        phone
                        if phone
                        else
                        t(
                            "contact_unavailable",
                            language
                        )
                    ),

                "website":
                    (
                        website
                        if website
                        else
                        ""
                    ),

                "map_url":
                    map_url

            })

        unique_results = []

        seen_names = set()

        for storage_item in storage_results:

            name_key = (
                storage_item["name"]
                .strip()
                .lower()
            )

            if name_key in seen_names:
                continue

            seen_names.add(
                name_key
            )

            unique_results.append(
                storage_item
            )

        def get_distance(storage_item):

            try:

                return float(
                    storage_item["distance"]
                    .replace(
                        " km",
                        ""
                    )
                    .replace(
                        " (demo)",
                        ""
                    )
                )

            except:

                return 999999

        unique_results.sort(
            key=get_distance
        )

        unique_results = (
            unique_results[:10]
        )

        if len(unique_results) == 0:

            unique_results = create_demo_storage(
                location,
                crop,
                language
            )

            storage_demo = True

        else:

            storage_demo = False

        return render_template(

            "result.html",

            show_storage_finder=True,

            storage_finder_location=location,
            storage_finder_crop=display_crop,

            storage_results=unique_results,

            storage_demo=storage_demo,

            language=language
        )

    except urllib.error.HTTPError as e:

        print(
            "STORAGE HTTP ERROR:",
            e.code
        )

        demo_results = create_demo_storage(
            location,
            crop,
            language
        )

        return render_template(

            "result.html",

            show_storage_finder=True,

            storage_finder_location=location,
            storage_finder_crop=display_crop,

            storage_results=demo_results,

            storage_demo=True,
            storage_error=True,

            language=language
        )

    except Exception as e:

        print(
            "STORAGE FINDER ERROR:",
            e
        )

        demo_results = create_demo_storage(
            location,
            crop,
            language
        )

        return render_template(

            "result.html",

            show_storage_finder=True,

            storage_finder_location=location,
            storage_finder_crop=display_crop,

            storage_results=demo_results,

            storage_demo=True,
            storage_error=True,

            language=language
        )


# =====================================================
# DEMO STORAGE DATA
# =====================================================

def create_demo_storage(
    location,
    crop,
    language="en"
):

    crop_name = translate_crop_name(
        crop,
        language
    )

    return [

        {
            "name":
                "Demo Krishi Cold Storage",

            "location":
                f"{location} Demo Area",

            "distance":
                "5.2 km",

            "type":
                "Cold Storage",

            "crops":
                t(
                    "storage_crop_search",
                    language,
                    crop=crop_name
                ),

            "rent":
                "₹2.50 / kg / month",

            "availability":
                t(
                    "available",
                    language
                ),

            "contact":
                "98XXXXXX76",

            "website":
                "",

            "map_url":
                ""
        },

        {
            "name":
                "Demo Farmer Storage Centre",

            "location":
                f"Near {location} Demo Area",

            "distance":
                "9.8 km",

            "type":
                "Farmer Storage Centre",

            "crops":
                t(
                    "storage_crop_search",
                    language,
                    crop=crop_name
                ),

            "rent":
                "₹1,500 / month",

            "availability":
                t(
                    "available",
                    language
                ),

            "contact":
                "98XXXXXX76",

            "website":
                "",

            "map_url":
                ""
        },

        {
            "name":
                "Demo Agri Warehouse",

            "location":
                f"{location} Agricultural Zone Demo",

            "distance":
                "14.6 km",

            "type":
                "Agricultural Warehouse",

            "crops":
                t(
                    "storage_crop_search",
                    language,
                    crop=crop_name
                ),

            "rent":
                "Contact facility",

            "availability":
                t(
                    "check_availability",
                    language
                ),

            "contact":
                "98XXXXXX76",

            "website":
                "",

            "map_url":
                ""
        }

    ]


# =====================================================
# SMART MARKET / MANDI
# =====================================================

@app.route(
    "/market",
    methods=["POST"]
)
def market():

    language = get_language()

    state = request.form.get(
        "market_state",
        ""
    ).strip()

    district = request.form.get(
        "market_district",
        ""
    ).strip()

    city = request.form.get(
        "market_city",
        ""
    ).strip()

    crop = request.form.get(
        "market_crop",
        ""
    ).strip()

    if not crop:

        return """
        <h2>⚠️ Please select a crop.</h2>
        <a href="/">← Go Back</a>
        """

    if not state:

        return """
        <h2>⚠️ Please enter the state.</h2>
        <a href="/">← Go Back</a>
        """

    try:

        market_result = get_market_prices(

            state=state,
            district=district,
            city=city,
            crop=crop,
            language=language

        )

        return render_template(

            "result.html",

            show_market=True,

            market_state=state,
            market_district=district,
            market_city=city,

            market_crop=translate_crop_name(
                crop,
                language
            ),

            market_results=market_result.get(
                "results",
                []
            ),

            market_data_level=market_result.get(
                "data_level",
                t(
                    "not_available",
                    language
                )
            ),

            market_date=market_result.get(
                "date",
                t(
                    "not_available",
                    language
                )
            ),

            market_message=market_result.get(
                "message",
                ""
            ),

            market_error=market_result.get(
                "error",
                False
            ),

            language=language
        )

    except Exception as e:

        print(
            "MARKET ERROR:",
            e
        )

        return render_template(

            "result.html",

            show_market=True,

            market_state=state,
            market_district=district,
            market_city=city,

            market_crop=translate_crop_name(
                crop,
                language
            ),

            market_results=[],

            market_data_level=t(
                "not_available",
                language
            ),

            market_date=t(
                "not_available",
                language
            ),

            market_message=t(
                "market_load_failed",
                language
            ),

            market_error=True,

            language=language
        )
        


# =====================================================
# MARKET DATA FUNCTION
# =====================================================

def get_market_prices(
    state,
    district,
    city,
    crop,
    language="en"
):

    api_key = os.getenv(
        "DATA_GOV_API_KEY"
    )

    resource_id = os.getenv(
        "DATA_GOV_RESOURCE_ID"
    )

    if not api_key or not resource_id:

        print(
            "MARKET API CONFIGURATION NOT FOUND"
        )

        return {

            "results": [],

            "data_level":
                t(
                    "not_available",
                    language
                ),

            "date":
                t(
                    "not_available",
                    language
                ),

            "message":
                t(
                    "market_config",
                    language
                ),

            "error":
                True

        }

    base_url = (
        "https://api.data.gov.in/resource/"
        + resource_id
    )

    if district:

        search_levels = [

            {
                "level": "District",

                "filters": {
                    "state": state,
                    "district": district,
                    "commodity": crop
                }
            },

            {
                "level": "State",

                "filters": {
                    "state": state,
                    "commodity": crop
                }
            }

        ]

    else:

        search_levels = [

            {
                "level": "State",

                "filters": {
                    "state": state,
                    "commodity": crop
                }
            }

        ]

    for level_info in search_levels:

        level = level_info["level"]

        filters = level_info["filters"]

        try:

            rows = request_market_api(

                base_url=base_url,

                api_key=api_key,

                filters=filters

            )

            if not rows:
                continue

            processed = process_market_rows(
                rows
            )

            if not processed:
                continue

            if district:

                district_filtered = []

                requested_district = (
                    district.strip().lower()
                )

                requested_state = (
                    state.strip().lower()
                )

                for item in processed:

                    item_district = (
                        item.get(
                            "district",
                            ""
                        )
                        .strip()
                        .lower()
                    )

                    item_state = (
                        item.get(
                            "state",
                            ""
                        )
                        .strip()
                        .lower()
                    )

                    district_match = (
                        item_district
                        ==
                        requested_district
                    )

                    state_match = (
                        not item_state
                        or
                        item_state
                        ==
                        requested_state
                    )

                    if (
                        district_match
                        and
                        state_match
                    ):

                        district_filtered.append(
                            item
                        )

                if district_filtered:

                    processed = district_filtered

                else:

                    if level == "District":

                        print(
                            "NO VERIFIED DISTRICT MATCH:",
                            district
                        )

                        continue

            latest_date = get_latest_market_date(
                processed
            )

            best_market = processed[0]

            requested_area_message = ""

            if city:

                requested_area_message = t(
                    "market_area_note",
                    language,
                    city=city
                )

            message = (
                t(
                    "market_data_found",
                    language,
                    level=level
                )
                + " "
                +
                t(
                    "market_best",
                    language,
                    market=best_market.get(
                        "market_name",
                        "Market"
                    ),
                    price=best_market.get(
                        "modal_price",
                        t(
                            "not_available",
                            language
                        )
                    )
                )
                +
                requested_area_message
            )

            return {

                "results":
                    processed,

                "data_level":
                    level,

                "date":
                    latest_date,

                "message":
                    message,

                "error":
                    False

            }

        except Exception as e:

            print(
                "MARKET LEVEL ERROR:",
                level,
                e
            )

            continue

    return {

        "results": [],

        "data_level":
            t(
                "not_available",
                language
            ),

        "date":
            t(
                "not_available",
                language
            ),

        "message":
            t(
                "market_no_data",
                language
            ),

        "error":
            False

    }


# =====================================================
# DATA.GOV.IN API REQUEST
# =====================================================

def request_market_api(
    base_url,
    api_key,
    filters
):

    params = {

        "api-key":
            api_key.strip(),

        "format":
            "json",

        "limit":
            100

    }

    for key, value in filters.items():

        if value:

            params[
                "filters[" + key + "]"
            ] = value

    query_string = urllib.parse.urlencode(
        params
    )

    url = (
        base_url
        + "?"
        + query_string
    )

    print(
        "MARKET API REQUEST:",
        url.replace(
            api_key,
            "HIDDEN_API_KEY"
        )
    )

    market_request = urllib.request.Request(

        url,

        headers={

            "User-Agent":
            "Smart-Krishi-AI-Project/1.0"

        }

    )

    with urllib.request.urlopen(
        market_request,
        timeout=20
    ) as response:

        data = json.loads(
            response.read().decode(
                "utf-8"
            )
        )

    return data.get(
        "records",
        []
    )


# =====================================================
# PROCESS MARKET ROWS
# =====================================================

def process_market_rows(
    rows
):

    processed = []

    for row in rows:

        market_name = get_row_value(
            row,
            [
                "market",
                "Market",
                "market_name",
                "Market Name"
            ]
        )

        commodity = get_row_value(
            row,
            [
                "commodity",
                "Commodity"
            ]
        )

        variety = get_row_value(
            row,
            [
                "variety",
                "Variety"
            ]
        )

        state = get_row_value(
            row,
            [
                "state",
                "State"
            ]
        )

        district = get_row_value(
            row,
            [
                "district",
                "District"
            ]
        )

        date = get_row_value(
            row,
            [
                "arrival_date",
                "Arrival_Date",
                "date",
                "Date"
            ]
        )

        min_price = get_row_value(
            row,
            [
                "min_price",
                "Min Price",
                "Min_Price"
            ]
        )

        max_price = get_row_value(
            row,
            [
                "max_price",
                "Max Price",
                "Max_Price"
            ]
        )

        modal_price = get_row_value(
            row,
            [
                "modal_price",
                "Modal Price",
                "Modal_Price"
            ]
        )

        if not market_name:
            continue

        min_value = parse_price(
            min_price
        )

        max_value = parse_price(
            max_price
        )

        modal_value = parse_price(
            modal_price
        )

        if (
            min_value is None
            and
            max_value is None
            and
            modal_value is None
        ):
            continue

        map_search_parts = []

        if market_name:
            map_search_parts.append(
                market_name
            )

        if district:
            map_search_parts.append(
                district
            )

        if state:
            map_search_parts.append(
                state
            )

        map_search_query = ", ".join(
            map_search_parts
        )

        map_url = (

            "https://www.google.com/maps/search/?api=1&query="

            +
            urllib.parse.quote_plus(
                map_search_query
            )

        )

        processed.append({

            "market":
                market_name,

            "market_name":
                market_name,

            "area":
                market_name,

            "commodity":
                commodity
                if commodity
                else
                "Not available",

            "variety":
                variety
                if variety
                else
                "Not available",

            "state":
                state
                if state
                else
                "Not available",

            "district":
                district
                if district
                else
                "Not available",

            "date":
                date
                if date
                else
                "Not available",

            "min_price":
                format_price(
                    min_value
                ),

            "max_price":
                format_price(
                    max_value
                ),

            "modal_price":
                format_price(
                    modal_value
                ),

            "map_url":
                map_url,

            "_min":
                min_value
                if min_value is not None
                else
                0,

            "_max":
                max_value
                if max_value is not None
                else
                0,

            "_modal":
                modal_value
                if modal_value is not None
                else
                0

        })

    processed.sort(

        key=lambda x:

            x["_modal"]
            if x["_modal"] > 0
            else
            x["_max"],

        reverse=True

    )

    if processed:

        for item in processed:

            item["best"] = False

        processed[0]["best"] = True

    processed = processed[:20]

    return processed


# =====================================================
# GET ROW VALUE
# =====================================================

def get_row_value(
    row,
    possible_keys
):

    for key in possible_keys:

        if key in row:

            value = row.get(
                key
            )

            if value is not None:

                return str(
                    value
                ).strip()

    row_keys = {
        str(k).lower(): k
        for k in row.keys()
    }

    for key in possible_keys:

        actual_key = row_keys.get(
            key.lower()
        )

        if actual_key is not None:

            value = row.get(
                actual_key
            )

            if value is not None:

                return str(
                    value
                ).strip()

    return ""


# =====================================================
# PARSE PRICE
# =====================================================

def parse_price(
    value
):

    if value is None:

        return None

    text = str(
        value
    ).strip()

    if not text:

        return None

    text = (
        text
        .replace(",", "")
        .replace("₹", "")
        .strip()
    )

    try:

        return float(
            text
        )

    except:

        return None


# =====================================================
# FORMAT PRICE
# =====================================================

def format_price(
    value
):

    if value is None:

        return "Not available"

    try:

        return (
            "₹"
            +
            f"{float(value):,.0f}"
            +
            " / quintal"
        )

    except:

        return "Not available"


# =====================================================
# GET LATEST MARKET DATE
# =====================================================

def get_latest_market_date(
    rows
):

    dates = []

    for row in rows:

        date = row.get(
            "date",
            ""
        )

        if date:

            dates.append(
                date
            )

    if not dates:

        return "Not available"

    try:

        return sorted(
            dates
        )[-1]

    except:

        return dates[0]


# =====================================================
# OPEN BROWSER
# =====================================================

def open_browser():

    webbrowser.open(
        "http://127.0.0.1:5000"
    )


# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":

    Timer(
        1,
        open_browser
    ).start()

    app.run(
        debug=True,
        use_reloader=False
    )

