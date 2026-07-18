from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# إعداد قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pharmacy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# جدول الأدوية المطور ليشمل الصور والوصف الثنائي
class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)       
    symptom = db.Column(db.String(500), nullable=False)    
    description = db.Column(db.Text, nullable=True)        
    price = db.Column(db.Integer, default=1000)            
    image_url = db.Column(db.String(300), nullable=True)   

# إعادة تهيئة البيانات لملء الأوصاف باللغتين معاً
with app.app_context():
    db.drop_all()  # حذف الجدول القديم لتحديث البيانات فوراً
    db.create_all()  
    
    comprehensive_meds = [
        # 1. ألم البطن والمغص
        Medicine(
            name="هيووسين بيوتيل بروميد (البدائل في اليمن: بسكوبان Buscopan، أو سبازموبان) / Hyoscine butylbromide", 
            symptom="ألم في البطن مغص تقلصات ألم معدة وجع بطن التواء مغص كلوي stomach ache pain cramps belly colic spasm", 
            description="مضاد للتقلصات والمغص، يهدئ عضلات الجهاز الهضمي. الجرعة: حبة قبل الأكل ثلاث مرات يومياً عند اللزوم. / Antispasmodic, relaxes GI tract muscles. Dosage: 1 tablet 3 times daily before meals when necessary.",
            price=1200,
            image_url="https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=200&q=80"
        ),
        # 2. الحموضة وحرقان المعدة
        Medicine(
            name="أوميبرازول (البدائل في اليمن: لوسك Losec، أو أوميز Omez) / Omeprazole", 
            symptom="حموضة حرقان حوضة حرقة معدة ارتجاع مريء ألم فم المعدة heartburn acidity stomach burn reflux", 
            description="تقليل إفراز أحماض المعدة وعلاج الحرقة والارتجاع. الجرعة: كبسولة واحدة صباحاً قبل الأكل بنصف ساعة. / Reduces stomach acid secretion & treats heartburn. Dosage: 1 capsule daily in the morning 30 minutes before breakfast.",
            price=2000,
            image_url="https://images.unsplash.com/photo-1584017911766-d451b3d0e843?w=200&q=80"
        ),
        # 3. الصداع والحمى والآلام العامة
        Medicine(
            name="باراسيتامول (البدائل في اليمن: فلوكام، بنادول Panadol، أو أدول) / Paracetamol", 
            symptom="صداع حمى ألم أسنان سخونة وجع راس ارتفاع حرارة headache fever toothache cold pain", 
            description="مسكن للألم وخافض للحرارة لطيف على المعدة. الجرعة: حبة أو حبتين بعد الأكل عند الحاجة. / Analgesic & antipyretic, gentle on stomach. Dosage: 1-2 tablets after meals when needed.",
            price=600,
            image_url="https://images.unsplash.com/photo-1550572017-edd951b55104?w=200&q=80"
        ),
        # 4. الزكام والرشح والحساسية
        Medicine(
            name="لوراتادين (البدائل في اليمن: كلاريتين Claritine، أو لورين) / Loratadine", 
            symptom="زكام رشح حساسية عطاس كحة حكة جفاف أنف سيلان flu allergy cold sneeze cough runny nose", 
            description="مضاد للحساسية ومخفف للرشح والعطاس بدون تسبب في النعاس. الجرعة: حبة واحدة مساءً قبل النوم. / Antihistamine for allergy & runny nose symptoms, non-drowsy. Dosage: 1 tablet daily at night before bedtime.",
            price=1500,
            image_url="https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=200&q=80"
        )
    ]
    db.session.bulk_save_objects(comprehensive_meds)
    db.session.commit()

def analyze_symptoms(user_text):
    if not user_text:
        return None
    all_medicines = Medicine.query.all()
    best_match = None
    max_matches = 0
    user_words = user_text.lower().split()
    
    for med in all_medicines:
        matches = 0
        for word in user_words:
            if word in med.symptom.lower():
                matches += 1
        if matches > max_matches:
            max_matches = matches
            best_match = med
    return best_match

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    user_input = ""
    if request.method == 'POST':
        user_input = request.form.get('symptoms', '')
        matched_medicine = analyze_symptoms(user_input)
        
        if matched_medicine:
            result = {
                "status": "success",
                "id": matched_medicine.id,
                "medicine_name": matched_medicine.name,
                "description": matched_medicine.description,
                "price": matched_medicine.price,
                "image_url": matched_medicine.image_url
            }
        else:
            result = {
                "status": "fail",
                "message": "عذراً، هذه الأعراض بحاجة لفحص سريري مباشر أو أن البديل الدوائي غير متوفر حالياً بمخازن الصيدليات اليمنية."
            }

    return render_template('index.html', result=result, user_input=user_input)

if __name__ == '__main__':
    app.run(debug=True)