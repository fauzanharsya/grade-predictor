import flask
from flask import Flask, request, render_template, jsonify, redirect, url_for
import joblib
import numpy as np
import pandas as pd # Pastikan pandas diimport
import traceback
import os
import math

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'models')
MODEL_FILE_PATH = os.path.join(MODEL_DIR, 'random_forest_original_model.pkl')

model = None
model_feature_names = []

def load_primary_model(model_path):
    try:
        if os.path.exists(model_path):
            print(f"* Mencoba memuat model dari: {model_path}")
            loaded_model = joblib.load(model_path)
            print(f"* Model berhasil dimuat dari {model_path}.")
            return loaded_model
        else:
            print(f"!! FATAL: File model tidak ditemukan di {model_path}")
            return None
    except Exception as e:
        print(f"!! FATAL: Error saat memuat model dari {model_path}: {e}")
        traceback.print_exc()
        return None

model = load_primary_model(MODEL_FILE_PATH)

if model is not None:
    model_feature_names = [
        'Internet_Access', 'Extracurricular_Activities', 'Peer_Influence',
        'Access_to_Resources', 'Teacher_Quality', 'Distance_from_Home',
        'Hours_Studied', 'Previous_Scores',
        'Attendance',
        'Tutoring_Sessions',
    ]
    print(f"* Fitur yang diharapkan model (Random Forest): {model_feature_names}")
else:
    print("!! FATAL: Model Random Forest tidak berhasil dimuat. Fitur prediksi tidak akan berfungsi.")

def preprocess_input(form_data):
    processed = {}
    internet_map = {'yes': 1, 'no': 0}
    extracurricular_map = {'yes': 1, 'no': 0}
    peer_influence_map = {'negative': 0, 'neutral': 1, 'positive': 2}
    resource_access_map = {'high': 0, 'low': 1, 'medium': 2}
    teacher_quality_map = {'high': 0, 'low': 1, 'medium': 2}
    distance_map = {'far': 0, 'moderate': 1, 'near': 2}

    try:
        processed['Internet_Access'] = internet_map.get(form_data.get('internetAccess'), 0)
        processed['Extracurricular_Activities'] = extracurricular_map.get(form_data.get('extracurricular'), 0)
        processed['Peer_Influence'] = peer_influence_map.get(form_data.get('peerInfluence'), 1)
        processed['Access_to_Resources'] = resource_access_map.get(form_data.get('resourceAccess'), 2)
        processed['Teacher_Quality'] = teacher_quality_map.get(form_data.get('teacherQuality'), 2)
        processed['Distance_from_Home'] = distance_map.get(form_data.get('distanceHome'), 1)
        processed['Hours_Studied'] = float(form_data.get('hoursStudied', 0) or 0)
        processed['Previous_Scores'] = float(form_data.get('previousScore', 0) or 0)
        processed['Tutoring_Sessions'] = float(form_data.get('tutoringSessions', 0) or 0)
        attendance_count = float(form_data.get('attendance', 0) or 0)
        total_sessions_count = float(form_data.get('totalSessions', 1) or 1)
        if total_sessions_count > 0:
            attendance_value = (attendance_count / total_sessions_count) * 100
        else:
            attendance_value = 0
        processed['Attendance'] = round(attendance_value)
    except ValueError as e:
        raise ValueError(f"Input tidak valid: {e}. Pastikan semua angka diisi dengan benar.")
    except Exception as e:
        raise e
    for feature in model_feature_names:
        if feature not in processed:
            processed[feature] = 0
    return processed

# --- ROUTE TETAP SAMA ---
@app.route('/')
@app.route('/home')
def halaman_utama():
    return render_template('HomePage.html')

@app.route('/prediksi')
def halaman_prediksi():
    if model is None:
        return render_template('hasil_prediksi.html',
                               error="Model prediksi utama tidak dapat dimuat. Fitur prediksi tidak tersedia.")
    return render_template('PredictionPage.html')

@app.route('/tips-belajar')
def halaman_tips():
    return render_template('StudyTips.html')

@app.route('/tentang')
def halaman_tentang():
    return render_template('AboutUs.html')

@app.route('/kontak')
def halaman_kontak():
    return render_template('Kontak.html')

@app.route('/proses-prediksi', methods=['POST'])
def proses_prediksi():
    if model is None:
        return render_template('hasil_prediksi.html',
                               error="Model prediksi tidak tersedia. Tidak dapat melakukan prediksi.")
    if request.method == 'POST':
        try:
            form_data = request.form
            print("* Menerima data form:", form_data.to_dict())

            processed_features_dict = preprocess_input(form_data)
            print("* Data setelah preprocessing:", processed_features_dict)

            # --- MODIFIKASI: Buat DataFrame dengan urutan kolom yang benar ---
            # 1. Buat DataFrame dari dictionary
            input_df = pd.DataFrame([processed_features_dict])
            # 2. Reindex untuk memastikan urutan dan nama kolom sesuai dengan saat training
            #    Ini juga akan menangani jika ada fitur yang hilang (akan diisi NaN atau fill_value jika dispesifikkan)
            #    atau fitur ekstra (akan diabaikan).
            #    Penting: fill_value=0 mungkin tidak selalu cocok untuk semua fitur jika ada yang hilang.
            #    Namun, fungsi preprocess_input Anda sudah mencoba memastikan semua fitur ada.
            input_df_reordered = input_df.reindex(columns=model_feature_names, fill_value=0)

            print("* DataFrame input untuk model:\n", input_df_reordered)
            # --- AKHIR MODIFIKASI ---

            # Lakukan prediksi menggunakan DataFrame
            prediction_raw = model.predict(input_df_reordered) # <-- Gunakan DataFrame di sini

            predicted_score_float = float(prediction_raw[0])
            predicted_score = math.ceil(predicted_score_float)
            predicted_score = max(0, min(100, predicted_score))
            
            print(f"* Skor mentah: {prediction_raw[0]}, Skor float: {predicted_score_float}, Skor dibulatkan ke atas: {predicted_score}")

            grade = ""
            if predicted_score == 0:
                grade = "F"
            elif 0 < predicted_score < 50:
                grade = "E"
            elif 50 <= predicted_score < 65:
                grade = "D"
            elif 65 <= predicted_score < 70:
                grade = "C"
            elif 70 <= predicted_score < 75:
                grade = "B-"
            elif 75 <= predicted_score < 80:
                grade = "B"
            elif 80 <= predicted_score < 85:
                grade = "B+"
            elif 85 <= predicted_score < 90:
                grade = "A-"
            elif 90 <= predicted_score <= 100:
                grade = "A"
            else:
                grade = "N/A"

            saran = ""
            if predicted_score >= 90:
                saran = "Luar biasa! Pertahankan fokus dan terus eksplorasi materi lebih dalam. Anda di jalur yang sangat tepat!"
            elif predicted_score >= 80:
                saran = "Hasil yang bagus! Identifikasi area yang masih bisa ditingkatkan sedikit lagi dan pertahankan kebiasaan belajar positif Anda."
            elif predicted_score >= 70:
                saran = "Cukup baik! Terus tingkatkan pemahaman konsep dasar dan latihan soal secara rutin untuk hasil yang lebih optimal."
            elif predicted_score >= 60:
                saran = "Sudah cukup, tapi masih banyak ruang untuk peningkatan. Coba evaluasi metode belajar Anda, mungkin perlu strategi baru atau tambahan waktu belajar."
            else:
                saran = "Jangan berkecil hati! Ini adalah kesempatan untuk mengidentifikasi tantangan utama. Fokus pada pemahaman fundamental, jangan ragu bertanya, dan cari sumber belajar tambahan."

            return render_template('hasil_prediksi.html',
                                   prediksi_skor=predicted_score,
                                   grade=grade,
                                   saran=saran)
        except ValueError as ve:
            print(f"!! Value Error saat proses: {ve}")
            traceback.print_exc()
            return render_template('hasil_prediksi.html',
                                   error=f"Input Data Tidak Valid: {ve}. Mohon periksa kembali isian Anda.")
        except KeyError as ke:
            print(f"!! Key Error saat proses: {ke}")
            traceback.print_exc()
            return render_template('hasil_prediksi.html',
                                   error=f"Kesalahan pada Data Input atau Konfigurasi Fitur: Kolom '{ke}' tidak ditemukan. Hubungi administrator.")
        except Exception as e:
            print(f"!! Terjadi Error Tak Terduga: {e}")
            traceback.print_exc()
            return render_template('hasil_prediksi.html',
                                   error="Terjadi kesalahan internal saat memproses prediksi. Silakan coba lagi nanti atau hubungi administrator.")
    return redirect(url_for('halaman_prediksi'))

if __name__ == '__main__':
    if model is None:
        print("!! PERINGATAN: APLIKASI BERJALAN TANPA MODEL PREDIKSI. FITUR PREDIKSI TIDAK AKAN BERFUNGSI. !!")
    app.run(debug=True, host='0.0.0.0', port=5000)