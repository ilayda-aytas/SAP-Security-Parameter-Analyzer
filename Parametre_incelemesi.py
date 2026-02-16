
import win32com.client
import pandas as pd
import subprocess
import time
# ==============================
# SAP PARAMETER SECURITY ANALYSIS
# ==============================
# SAP bağlantı parametreleri
SAP_USER = ""
SAP_PASSWORD = ""
SAP_ASHOST = ""
SAP_SYSNR = ""
SAP_CLIENT = ""
SAP_LANG = ""
def sap_connect_and_extract():
    """SAP'ye bağlan ve RSPARAM ile güvenlik parametrelerini çek"""
    print("SAP bağlantısı başlatılıyor...")
    
    # SAP Logon başlat
    saplogon_path = r"\\SapGui\\saplogon.exe"  #path
    subprocess.Popen(saplogon_path)
    time.sleep(5)
    # Excel'den hedef parametreleri oku
    param_df = pd.read_excel("Parametreler.xlsx")
    param_list = param_df["Parametre Adı"].dropna().tolist()
    print(f"{len(param_list)} güvenlik parametresi analiz edilecek")
    # SAP GUI bağlantısı
    SapGuiAuto = win32com.client.GetObject("SAPGUI")
    application = SapGuiAuto.GetScriptingEngine
    connection = application.OpenConnection("  ", True)  #SAP Name
    session = connection.Children(0)
    # SAP login
    print("SAP sistemine giriş yapılıyor...")
    session.findById("wnd[0]/usr/txtRSYST-BNAME").text = SAP_USER
    session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = SAP_PASSWORD
    session.findById("wnd[0]/usr/txtRSYST-MANDT").text = SAP_CLIENT
    session.findById("wnd[0]/usr/txtRSYST-LANGU").text = SAP_LANG
    session.findById("wnd[0]").sendVKey(0)
    # RSPARAM çalıştır
    print("RSPARAM transaction başlatılıyor...")
    session.findById("wnd[0]").maximize()
    session.findById("wnd[0]/tbar[0]/okcd").text = "SA38"
    session.findById("wnd[0]").sendVKey(0)
    time.sleep(5)
    session.findById("wnd[0]/usr/ctxtRS38M-PROGRAMM").text = "RSPARAM"
    session.findById("wnd[0]/tbar[1]/btn[8]").press()
    session.findById("wnd[0]/tbar[1]/btn[8]").press()
    results = []
    processed_params = 0
    not_found_params = []
    for param in param_list:
        try:
            print(f"Parametre analiz ediliyor: {param}")
            
            # Filtre ekranına git
            session.findById("wnd[0]/tbar[1]/btn[29]").press()
            session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_FILTER_CRITERIA:0600/btnAPP_WL_SING").press()
            session.findById("wnd[1]/usr/subSUB_CONFIGURATION:SAPLSALV_CUL_FILTER_CRITERIA:0600/btn600_BUTTON").press()
            time.sleep(1)
            # Parametreyi gir
            try:
                session.findById("wnd[2]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").text = param
                session.findById("wnd[2]/tbar[0]/btn[0]").press()
                time.sleep(1)
            except AttributeError:
                print(f"UYARI: Parametre girişi başarısız: {param}")
                session.findById("wnd[2]/tbar[0]/btn[12]").press()
                not_found_params.append(param)
                continue
            # Grid'den değerleri oku
            try:
                grid = session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell")
                row_count = grid.RowCount
                
                if row_count == 0:
                    print(f"UYARI: Parametre bulunamadı: {param}")
                    not_found_params.append(param)
                    # Bulunamayan parametreyi de sonuçlara ekle
                    results.append({
                        "Parametre": param,
                        "User-Defined Value": "",
                        "System Default Value": "",
                        "Current Value": "",
                        "Status": "NOT_FOUND"
                    })
                else:
                    param_found = False
                    for i in range(row_count):
                        param_name = grid.GetCellValue(i, "PAR_NAME")
                        user_val = grid.GetCellValue(i, "PAR_USER_WERT")
                        default_val = grid.GetCellValue(i, "PAR_DEFAULT_WERT1")
                        current_val = user_val if user_val else default_val
                        results.append({
                            "Parametre": param_name,
                            "User-Defined Value": user_val,
                            "System Default Value": default_val,
                            "Current Value": current_val,
                            "Status": "FOUND"
                        })
                        param_found = True
                    
                    if param_found:
                        processed_params += 1
            except Exception as grid_error:
                print(f"Grid okuma hatası {param}: {grid_error}")
                not_found_params.append(param)
                results.append({
                    "Parametre": param,
                    "User-Defined Value": "",
                    "System Default Value": "",
                    "Current Value": "",
                    "Status": "NOT_FOUND"
                })
            # Filtreyi temizle
            try:
                session.findById("wnd[0]/tbar[1]/btn[29]").press()
                session.findById("wnd[1]/tbar[0]/btn[12]").press()
            except:
                pass
        except Exception as e:
            print(f"HATA: {param} -> {e}")
            not_found_params.append(param)
            results.append({
                "Parametre": param,
                "User-Defined Value": "",
                "System Default Value": "",
                "Current Value": "",
                "Status": "ERROR"
            })
            continue
    # SAP bağlantısını kapat
    try:
        session.findById("wnd[0]").close()
    except:
        pass
    
    print(f"SAP bağlantısı kapatıldı. {processed_params} parametre başarıyla çekildi.")
    if not_found_params:
        print(f"Bulunamayan parametreler: {not_found_params}")
    
    return results
def security_advice_engine(sap_results):
    """SAP güvenlik tavsiyeleri motoru"""
    print("\nGüvenlik analizi başlıyor...")
    
    # Excel dosyalarını oku
    try:
        param_df = pd.read_excel("parametreler.xlsx")
        deneme_df = pd.DataFrame(sap_results)
    except FileNotFoundError as e:
        print(f"HATA: Excel dosyası bulunamadı: {e}")
        return None
    # Güvenlik tavsiye veritabanını hazırla
    security_database = {}
    for idx, row in param_df.iterrows():
        param_name = row["Parametre Adı"]
        if pd.notna(param_name):
            security_database[param_name] = {
                "recommended_value": row.get("Önerilen Değer", ""),
                "advice_low": row.get("Tavsiye (Düşükse)", ""),
                "advice_different": row.get("Tavsiye (Yüksekse/Farklıysa)", ""), 
                "advice_same": row.get("Tavsiye (Aynıysa)", "")
            }
    print(f"Güvenlik veritabanında {len(security_database)} parametre tanımı yüklendi")
    # Her parametre için güvenlik analizi yap
    security_advice_list = []
    recommended_value_list = []
    comparison_status_list = []
    
    for idx, row in deneme_df.iterrows():
        param_name = row["Parametre"]
        current_value = row["Current Value"]
        status = row.get("Status", "FOUND")
        
        # Güvenlik veritabanından parametre bilgilerini al
        param_security_info = security_database.get(param_name, {})
        
        if status in ["NOT_FOUND", "ERROR"]:
            advice = f"Parametre SAP sisteminde bulunamadı - Status: {status}"
            recommended_value = param_security_info.get("recommended_value", "")
            comparison_status = "NOT_FOUND"
        elif not param_security_info:
            advice = "Bu parametre güvenlik veritabanında tanımlı değil"
            recommended_value = ""
            comparison_status = "NO_RECOMMENDATION"
        else:
            recommended_value = param_security_info.get("recommended_value", "")
            advice_low = param_security_info.get("advice_low", "")
            advice_different = param_security_info.get("advice_different", "")
            advice_same = param_security_info.get("advice_same", "")
            
            # Güvenlik karşılaştırma algoritması
            advice, comparison_status = analyze_security_parameter(
                param_name, current_value, recommended_value,
                advice_same, advice_different, advice_low
            )
        
        security_advice_list.append(advice)
        recommended_value_list.append(recommended_value)
        comparison_status_list.append(comparison_status)
    # Sonuçları Excel'e kaydet - İSTENEN FORMAT
    final_df = pd.DataFrame({
        "Parametre": deneme_df["Parametre"],
        "Current Value": deneme_df["Current Value"],
        "System Default Value": deneme_df["System Default Value"],
        "Recommended Value": recommended_value_list,
        "Comparison Status": comparison_status_list,
        "Security Advice": security_advice_list
    })
    
    final_df.to_excel("security_analysis_report.xlsx", index=False)
    
    print(f"\nGÜVENLİK ANALİZ RAPORU:")
    print(f"  Toplam analiz edilen parametre: {len(security_advice_list)}")
    print(f"  Bulunan parametreler: {len([s for s in comparison_status_list if s not in ['NOT_FOUND', 'NO_RECOMMENDATION']])}")
    print(f"  Bulunamayan parametreler: {len([s for s in comparison_status_list if s == 'NOT_FOUND'])}")
    
    return final_df
def analyze_security_parameter(param_name, current_val, recommended_val, advice_same, advice_different, advice_low):

    # Boş değer kontrolü
    if pd.isna(current_val) or current_val == "" or pd.isna(recommended_val) or recommended_val == "":
        return "Parametre değeri veya önerilen değer eksik - manuel kontrol gerekli", "INCOMPLETE_DATA"
    
    # Tavsiye metinlerini kontrol et
    if pd.isna(advice_same) and pd.isna(advice_different) and pd.isna(advice_low):
        return "Bu parametre için güvenlik tavsiyesi tanımlanmamış", "NO_ADVICE"
    
    try:
        # Sayısal karşılaştırma
        current_numeric = float(str(current_val).replace(",", "."))
        recommended_numeric = float(str(recommended_val).replace(",", "."))
        
        if current_numeric == recommended_numeric:
            # AYNI DURUM: Tavsiye (Aynıysa) kolonundan tavsiye al
            advice = advice_same if not pd.isna(advice_same) else "Güvenlik parametresi önerilen değerde"
            return advice, "SAME"
        elif current_numeric > recommended_numeric:
            # YÜKSEK/FARKLI DURUM: Tavsiye (Yüksekse/Farklıysa) kolonundan tavsiye al
            advice = advice_different if not pd.isna(advice_different) else "Değer önerilen güvenlik seviyesinden yüksek"
            return advice, "HIGH"
        else:  # current_numeric < recommended_numeric
            # DÜŞÜK DURUM: Tavsiye (Düşükse) kolonundan tavsiye al
            advice = advice_low if not pd.isna(advice_low) else "Değer önerilen güvenlik seviyesinden düşük"
            return advice, "LOW"
            
    except (ValueError, TypeError):
        # String karşılaştırması
        if str(current_val).strip().upper() == str(recommended_val).strip().upper():
            # AYNI DURUM: Tavsiye (Aynıysa) kolonundan tavsiye al
            advice = advice_same if not pd.isna(advice_same) else "Güvenlik parametresi uygun durumda"
            return advice, "SAME"
        else:
            # FARKLI DURUM: Tavsiye (Yüksekse/Farklıysa) kolonundan tavsiye al
            advice = advice_different if not pd.isna(advice_different) else "Parametre değeri güvenlik önerisinden farklı"
            return advice, "DIFFERENT"
# ==============================
# main
# ==============================
if __name__ == "__main__":
    print("=" * 60)
    print("SAP SECURITY PARAMETER ANALYSIS TOOL")
    print("=" * 60)
    
    try:
        # 1. SAP'den güvenlik parametrelerini çek
        sap_results = sap_connect_and_extract()
        
        if not sap_results:
            print("HATA: SAP'den veri alınamadı!")
            exit(1)
            
        print(f"\n{len(sap_results)} güvenlik parametresi SAP'den işlendi")
        
        # 2. Güvenlik analizi yap
        final_report = security_advice_engine(sap_results)
        
        if final_report is not None:
            print(f"\n✅ Güvenlik analizi tamamlandı!")
            print("📊 Detaylı rapor: 'security_analysis_report.xlsx'")
        else:
            print("❌ Güvenlik analizi başarısız!")
            
    except Exception as e:
        print(f"KRİTİK HATA: {e}")
        print("Program sonlandırılıyor...")
    
    print("\n" + "=" * 60)
    print("SAP SECURITY ANALYSIS COMPLETED")
    print("=" * 60)
