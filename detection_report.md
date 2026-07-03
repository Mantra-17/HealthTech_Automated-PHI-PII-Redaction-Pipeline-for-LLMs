# PHI Redaction Detection Report

This report documents the detailed numbers, categories, and positions of all Protected Health Information (PHI) entities detected across the 20 clinical notes.

## 1. High-Level Summary Metrics

* **Total Notes Scanned:** 20
* **Total PHI Ground Truth Items:** 209
* **Total Entities Detected:** 207
* **True Positives (TP):** 201
* **False Positives (FP):** 6
* **False Negatives (FN):** 8
* **Global Precision:** 97.10%
* **Global Recall:** 96.17%
* **Global F1-Score:** 96.63%

## 2. Global Entity Class Frequencies

| Entity Category | Count Detected | Description / Mapped Types |
| :--- | :---: | :--- |
| **DATE** | 32 | Mapped to de-identification pipeline standard |
| **PERSON** | 30 | Mapped to de-identification pipeline standard |
| **EMAIL** | 17 | Mapped to de-identification pipeline standard |
| **MRN** | 16 | Mapped to de-identification pipeline standard |
| **LICENSE** | 14 | Mapped to de-identification pipeline standard |
| **US_DRIVER_LICENSE** | 13 | Mapped to de-identification pipeline standard |
| **INSURANCE** | 13 | Mapped to de-identification pipeline standard |
| **PHONE** | 12 | Mapped to de-identification pipeline standard |
| **LOCATION** | 12 | Mapped to de-identification pipeline standard |
| **DATE_TIME** | 11 | Mapped to de-identification pipeline standard |
| **ORGANIZATION** | 11 | Mapped to de-identification pipeline standard |
| **AADHAAR** | 8 | Mapped to de-identification pipeline standard |
| **SSN** | 8 | Mapped to de-identification pipeline standard |
| **IP** | 4 | Mapped to de-identification pipeline standard |
| **URL** | 3 | Mapped to de-identification pipeline standard |
| **PHONE_NUMBER** | 2 | Mapped to de-identification pipeline standard |
| **ZIP** | 1 | Mapped to de-identification pipeline standard |

## 3. Per-Note Summary Statistics

| Note ID | Word Count | PHI Ground Truth | Detected | True Positives (TP) | False Positives (FP) | False Negatives (FN) | Recall |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| NOTE_001 | 29 | 12 | 12 | 12 | 0 | 0 | 100.00% |
| NOTE_002 | 32 | 12 | 12 | 12 | 0 | 0 | 100.00% |
| NOTE_003 | 27 | 12 | 11 | 11 | 0 | 1 | 91.67% |
| NOTE_004 | 28 | 12 | 11 | 11 | 0 | 1 | 91.67% |
| NOTE_005 | 33 | 14 | 13 | 13 | 0 | 1 | 92.86% |
| NOTE_006 | 33 | 11 | 11 | 11 | 0 | 0 | 100.00% |
| NOTE_007 | 40 | 9 | 9 | 9 | 0 | 0 | 100.00% |
| NOTE_008 | 26 | 9 | 9 | 9 | 0 | 0 | 100.00% |
| NOTE_009 | 27 | 10 | 10 | 10 | 0 | 0 | 100.00% |
| NOTE_010 | 41 | 11 | 11 | 11 | 0 | 0 | 100.00% |
| NOTE_011 | 25 | 10 | 10 | 10 | 0 | 0 | 100.00% |
| NOTE_012 | 28 | 10 | 10 | 10 | 0 | 0 | 100.00% |
| NOTE_013 | 39 | 14 | 12 | 12 | 0 | 2 | 85.71% |
| NOTE_014 | 31 | 12 | 12 | 12 | 0 | 0 | 100.00% |
| NOTE_015 | 43 | 13 | 13 | 13 | 0 | 0 | 100.00% |
| NOTE_016 | 56 | 12 | 11 | 11 | 1 | 1 | 91.67% |
| NOTE_017 | 50 | 7 | 8 | 6 | 2 | 1 | 85.71% |
| NOTE_018 | 48 | 9 | 9 | 8 | 1 | 1 | 88.89% |
| NOTE_019 | 40 | 6 | 8 | 6 | 1 | 0 | 100.00% |
| NOTE_020 | 42 | 4 | 5 | 4 | 1 | 0 | 100.00% |

## 4. Itemized Detections (All Notes)

| Note ID | Entity Category | Detected Text Value | Character Span (Start-End) |
| :--- | :--- | :--- | :---: |
| NOTE_001 | **PERSON** | `Rahul Sharma` | 8-20 |
| NOTE_001 | **DATE** | `14/02/1985` | 27-37 |
| NOTE_001 | **MRN** | `MRN-12345` | 39-48 |
| NOTE_001 | **DATE_TIME** | `INS-111111-A.` | 69-82 |
| NOTE_001 | **PHONE** | `+91-98765-43210` | 92-107 |
| NOTE_001 | **EMAIL** | `rahul.sharma@gmail.com` | 115-137 |
| NOTE_001 | **AADHAAR** | `1234 5678 9012` | 160-174 |
| NOTE_001 | **PERSON** | `Driver` | 176-182 |
| NOTE_001 | **LICENSE** | `MH-2024-7890` | 193-205 |
| NOTE_001 | **LOCATION** | `MG Road` | 219-226 |
| NOTE_001 | **LOCATION** | `Mumbai` | 228-234 |
| NOTE_001 | **US_DRIVER_LICENSE** | `400001` | 235-241 |
| NOTE_002 | **PERSON** | `Sarah Johnson` | 8-21 |
| NOTE_002 | **DATE** | `June 14 1989` | 27-39 |
| NOTE_002 | **DATE** | `June 14 2026` | 52-64 |
| NOTE_002 | **MRN** | `MRN-54321` | 66-75 |
| NOTE_002 | **PHONE** | `(312) 555-7812` | 84-98 |
| NOTE_002 | **EMAIL** | `sarah.j@outlook.com` | 107-126 |
| NOTE_002 | **SSN** | `123-45-6789` | 133-144 |
| NOTE_002 | **INSURANCE** | `INS-222222-B` | 162-174 |
| NOTE_002 | **LICENSE** | `CA-2025-98765` | 184-197 |
| NOTE_002 | **ORGANIZATION** | `Pine St` | 213-220 |
| NOTE_002 | **LOCATION** | `Chicago` | 222-229 |
| NOTE_002 | **ZIP** | `60614` | 234-239 |
| NOTE_003 | **PERSON** | `Vikram Iyer` | 8-19 |
| NOTE_003 | **DATE** | `1980-05-12` | 26-36 |
| NOTE_003 | **DATE** | `2026-07-15` | 51-61 |
| NOTE_003 | **MRN** | `MRN-99999` | 63-72 |
| NOTE_003 | **US_DRIVER_LICENSE** | `9123456789` | 83-93 |
| NOTE_003 | **EMAIL** | `vikram.iyer@health.in` | 102-123 |
| NOTE_003 | **AADHAAR** | `987654321234` | 134-146 |
| NOTE_003 | **ORGANIZATION** | `INS-333333-C. Medical` | 169-190 |
| NOTE_003 | **LICENSE** | `KA-2023-54321` | 200-213 |
| NOTE_003 | **LOCATION** | `Lake Road` | 226-235 |
| NOTE_003 | **US_DRIVER_LICENSE** | `560034` | 247-253 |
| NOTE_004 | **PERSON** | `Emily Turner` | 8-20 |
| NOTE_004 | **DATE** | `09/12/1992` | 27-37 |
| NOTE_004 | **DATE** | `03/19/2026` | 50-60 |
| NOTE_004 | **MRN** | `MRN-22222` | 62-71 |
| NOTE_004 | **PHONE** | `646-555-3819` | 80-92 |
| NOTE_004 | **EMAIL** | `emily.turner@hospital.com` | 101-126 |
| NOTE_004 | **SSN** | `987-12-3456` | 133-144 |
| NOTE_004 | **INSURANCE** | `INS-444444-D` | 157-169 |
| NOTE_004 | **LICENSE** | `NY-2022-11111` | 187-200 |
| NOTE_004 | **LOCATION** | `New York` | 226-234 |
| NOTE_004 | **DATE_TIME** | `10011` | 239-244 |
| NOTE_005 | **PERSON** | `Abdul Khan` | 8-18 |
| NOTE_005 | **DATE** | `1978-08-22` | 24-34 |
| NOTE_005 | **DATE** | `2026-06-02` | 49-59 |
| NOTE_005 | **MRN** | `MRN-33333` | 61-70 |
| NOTE_005 | **PHONE** | `+91-99887-66554` | 79-94 |
| NOTE_005 | **EMAIL** | `abdul.khan@care.in` | 103-121 |
| NOTE_005 | **AADHAAR** | `456712348890` | 132-144 |
| NOTE_005 | **INSURANCE** | `INS-555555-E` | 157-169 |
| NOTE_005 | **LICENSE** | `RJ-2021-2222` | 179-191 |
| NOTE_005 | **LOCATION** | `Residency Rd` | 205-217 |
| NOTE_005 | **US_DRIVER_LICENSE** | `302001` | 226-232 |
| NOTE_005 | **IP** | `10.14.22.9` | 260-270 |
| NOTE_005 | **URL** | `www.citycare.in/portal.` | 284-307 |
| NOTE_006 | **PERSON** | `Laura Mitchell` | 8-22 |
| NOTE_006 | **DATE** | `October 10 1975` | 28-43 |
| NOTE_006 | **DATE** | `April 16 2026` | 58-71 |
| NOTE_006 | **MRN** | `MRN-44444` | 73-82 |
| NOTE_006 | **PHONE** | `(415) 555-2840` | 91-105 |
| NOTE_006 | **EMAIL** | `l.mitchell@bay.net` | 114-132 |
| NOTE_006 | **SSN** | `533-18-6245` | 139-150 |
| NOTE_006 | **ORGANIZATION** | `INS-666666-F. License` | 169-190 |
| NOTE_006 | **LICENSE** | `CA-2026-33333` | 191-204 |
| NOTE_006 | **DATE_TIME** | `94107` | 216-221 |
| NOTE_006 | **IP** | `172.16.44.101` | 251-264 |
| NOTE_007 | **DATE** | `1965-03-12` | 29-39 |
| NOTE_007 | **DATE** | `2026-05-10` | 54-64 |
| NOTE_007 | **MRN** | `MRN-55555` | 66-75 |
| NOTE_007 | **PHONE** | `206-555-0144` | 84-96 |
| NOTE_007 | **EMAIL** | `john.parkinson@clinic.org` | 105-130 |
| NOTE_007 | **SSN** | `667-24-8931` | 137-148 |
| NOTE_007 | **INSURANCE** | `INS-777777-G` | 158-170 |
| NOTE_007 | **LICENSE** | `WA-2025-44444` | 180-193 |
| NOTE_007 | **DATE_TIME** | `98101` | 205-210 |
| NOTE_008 | **PERSON** | `Neha Desai` | 8-18 |
| NOTE_008 | **DATE** | `11/01/1993` | 25-35 |
| NOTE_008 | **MRN** | `MRN-77777` | 37-46 |
| NOTE_008 | **INSURANCE** | `INS-888888-H` | 56-68 |
| NOTE_008 | **PHONE** | `+91 98765 12345` | 79-94 |
| NOTE_008 | **EMAIL** | `neha.desai@apollo.com` | 102-123 |
| NOTE_008 | **AADHAAR** | `2345 6789 1201` | 134-148 |
| NOTE_008 | **ORGANIZATION** | `License GJ-2024-55555` | 150-171 |
| NOTE_008 | **US_DRIVER_LICENSE** | `380009` | 211-217 |
| NOTE_009 | **PERSON** | `Robert Hayes` | 8-20 |
| NOTE_009 | **DATE** | `May 05 1970` | 26-37 |
| NOTE_009 | **DATE** | `June 05 2026` | 50-62 |
| NOTE_009 | **MRN** | `MRN-91111` | 64-73 |
| NOTE_009 | **PHONE** | `(202) 555-2711` | 82-96 |
| NOTE_009 | **EMAIL** | `robert.hayes@metro.us` | 105-126 |
| NOTE_009 | **SSN** | `111-22-3333` | 133-144 |
| NOTE_009 | **INSURANCE** | `INS-999999-I` | 161-173 |
| NOTE_009 | **LICENSE** | `DC-2023-66666` | 183-196 |
| NOTE_009 | **DATE_TIME** | `20009` | 203-208 |
| NOTE_010 | **PERSON** | `Kavya Menon` | 8-19 |
| NOTE_010 | **DATE** | `12-06-2026` | 26-36 |
| NOTE_010 | **DATE** | `05/12/1988` | 55-65 |
| NOTE_010 | **MRN** | `MRN-66666` | 67-76 |
| NOTE_010 | **US_DRIVER_LICENSE** | `9765432109` | 85-95 |
| NOTE_010 | **EMAIL** | `kavya.menon@skin.in` | 103-122 |
| NOTE_010 | **AADHAAR** | `1122 3344 5566` | 133-147 |
| NOTE_010 | **INSURANCE** | `INS-123456-J` | 156-168 |
| NOTE_010 | **LICENSE** | `KL-2022-77777` | 178-191 |
| NOTE_010 | **LOCATION** | `Green Park` | 205-215 |
| NOTE_010 | **DATE_TIME** | `Kochi 682020` | 217-229 |
| NOTE_011 | **PERSON** | `Jacob Miller` | 8-20 |
| NOTE_011 | **DATE** | `07/21/1982` | 27-37 |
| NOTE_011 | **MRN** | `MRN-77721` | 39-48 |
| NOTE_011 | **INSURANCE** | `INS-234567-K` | 58-70 |
| NOTE_011 | **PHONE** | `718-555-6620` | 81-93 |
| NOTE_011 | **EMAIL** | `jacob.miller@east.org` | 101-122 |
| NOTE_011 | **SSN** | `314-55-9002` | 129-140 |
| NOTE_011 | **LICENSE** | `NY-2021-88888` | 150-163 |
| NOTE_011 | **LOCATION** | `New York` | 189-197 |
| NOTE_011 | **DATE_TIME** | `10065` | 202-207 |
| NOTE_012 | **PERSON** | `Isha Gupta` | 8-18 |
| NOTE_012 | **DATE** | `09/06/2026` | 25-35 |
| NOTE_012 | **DATE** | `14/08/1995` | 47-57 |
| NOTE_012 | **MRN** | `MRN-24567` | 59-68 |
| NOTE_012 | **INSURANCE** | `INS-345678-L` | 77-89 |
| NOTE_012 | **PHONE** | `+91 90123 45678` | 100-115 |
| NOTE_012 | **EMAIL** | `isha.gupta@care.in` | 123-141 |
| NOTE_012 | **AADHAAR** | `7788 9900 1122` | 152-166 |
| NOTE_012 | **ORGANIZATION** | `License UP-2025-99999` | 168-189 |
| NOTE_012 | **US_DRIVER_LICENSE** | `226001` | 224-230 |
| NOTE_013 | **PERSON** | `Harpreet Singh` | 8-22 |
| NOTE_013 | **DATE** | `1991-03-18` | 28-38 |
| NOTE_013 | **DATE** | `18-03-2026` | 51-61 |
| NOTE_013 | **MRN** | `MRN-34220` | 63-72 |
| NOTE_013 | **INSURANCE** | `INS-456789-M` | 82-94 |
| NOTE_013 | **US_DRIVER_LICENSE** | `8899011223` | 103-113 |
| NOTE_013 | **EMAIL** | `harpreet.singh@spine.in` | 122-145 |
| NOTE_013 | **AADHAAR** | `6655 4433 2211` | 156-170 |
| NOTE_013 | **LICENSE** | `CH-2020-00111` | 181-194 |
| NOTE_013 | **US_DRIVER_LICENSE** | `160017` | 230-236 |
| NOTE_013 | **PERSON** | `Harpreet Singh` | 245-259 |
| NOTE_013 | **US_DRIVER_LICENSE** | `8899011223` | 310-320 |
| NOTE_014 | **PERSON** | `Matthew Clark` | 8-21 |
| NOTE_014 | **DATE** | `August 22 1983` | 27-41 |
| NOTE_014 | **DATE** | `February 3 2026` | 54-69 |
| NOTE_014 | **MRN** | `MRN-60991` | 71-80 |
| NOTE_014 | **PHONE** | `(503) 555-1299` | 89-103 |
| NOTE_014 | **EMAIL** | `m.clark@rainier.com` | 112-131 |
| NOTE_014 | **SSN** | `808-33-4501` | 138-149 |
| NOTE_014 | **INSURANCE** | `INS-567890-N` | 159-171 |
| NOTE_014 | **LICENSE** | `OR-2024-22222` | 181-194 |
| NOTE_014 | **PERSON** | `Alder St` | 208-216 |
| NOTE_014 | **LOCATION** | `Portland` | 218-226 |
| NOTE_014 | **DATE_TIME** | `97205` | 231-236 |
| NOTE_015 | **PERSON** | `Farah Ali` | 8-17 |
| NOTE_015 | **DATE** | `1996-05-18` | 23-33 |
| NOTE_015 | **DATE** | `13/07/2026` | 70-80 |
| NOTE_015 | **MRN** | `MRN-80818` | 82-91 |
| NOTE_015 | **US_DRIVER_LICENSE** | `9345678901` | 100-110 |
| NOTE_015 | **EMAIL** | `farah.ali@metro.in` | 119-137 |
| NOTE_015 | **AADHAAR** | `9900 7766 5544` | 148-162 |
| NOTE_015 | **INSURANCE** | `INS-678901-O` | 172-184 |
| NOTE_015 | **LICENSE** | `MH-2025-11223` | 195-208 |
| NOTE_015 | **ORGANIZATION** | `101 Palm Residency` | 219-237 |
| NOTE_015 | **DATE_TIME** | `Pune 411001` | 239-250 |
| NOTE_015 | **IP** | `192.168.10.150` | 310-324 |
| NOTE_015 | **URL** | `www.metrohospital.in/telehealth.` | 349-381 |
| NOTE_016 | **PERSON** | `John Smith` | 9-19 |
| NOTE_016 | **DATE** | `14/02/1985` | 35-45 |
| NOTE_016 | **DATE** | `05/06/2026` | 56-66 |
| NOTE_016 | **PHONE** | `(555) 019-2834` | 77-91 |
| NOTE_016 | **SSN** | `666-29-9012` | 97-108 |
| NOTE_016 | **LOCATION** | `MG Road` | 121-128 |
| NOTE_016 | **LOCATION** | `Mumbai` | 130-136 |
| NOTE_016 | **ORGANIZATION** | `Maharashtra 400001` | 138-156 |
| NOTE_016 | **PERSON** | `Emily Carter` | 182-194 |
| NOTE_016 | **DATE_TIME** | `4 days` | 283-289 |
| NOTE_016 | **PERSON** | `Emily Carter` | 377-389 |
| NOTE_017 | **PERSON** | `Rahul Verma
Age` | 14-29 |
| NOTE_017 | **MRN** | `MRN-998822` | 57-67 |
| NOTE_017 | **DATE** | `01/06/2026` | 78-88 |
| NOTE_017 | **EMAIL** | `rahul.verma@outlook.com` | 96-119 |
| NOTE_017 | **PHONE_NUMBER** | `91-98765-43210` | 128-142 |
| NOTE_017 | **ORGANIZATION** | `ECG` | 238-241 |
| NOTE_017 | **PERSON** | `Anil Mehta` | 307-317 |
| NOTE_017 | **ORGANIZATION** | `the Cardiology Wing of` | 321-343 |
| NOTE_018 | **PERSON** | `Sarah Johnson` | 6-19 |
| NOTE_018 | **INSURANCE** | `INS-789012-A` | 42-54 |
| NOTE_018 | **ORGANIZATION** | `Home Address` | 106-118 |
| NOTE_018 | **LOCATION** | `Delhi` | 136-141 |
| NOTE_018 | **US_DRIVER_LICENSE** | `110001` | 142-148 |
| NOTE_018 | **PERSON** | `Mike Johnson` | 168-180 |
| NOTE_018 | **US_DRIVER_LICENSE** | `9123456780` | 199-209 |
| NOTE_018 | **PERSON** | `Priya Nair` | 235-245 |
| NOTE_018 | **LICENSE** | `MH-2024-7890` | 259-271 |
| NOTE_019 | **DATE** | `June 12, 2026` | 6-19 |
| NOTE_019 | **PERSON** | `Robert 'Bob'` | 29-41 |
| NOTE_019 | **PERSON** | `Taylor` | 42-48 |
| NOTE_019 | **PHONE_NUMBER** | `09-18-1972` | 55-65 |
| NOTE_019 | **ORGANIZATION** | `IP Address of Device` | 67-87 |
| NOTE_019 | **IP** | `192.168.1.104` | 89-102 |
| NOTE_019 | **EMAIL** | `rtaylor72@yahoo.com` | 110-129 |
| NOTE_019 | **PERSON** | `Sarah Jenkins` | 280-293 |
| NOTE_020 | **PERSON** | `Alice Green
Age` | 9-24 |
| NOTE_020 | **DATE** | `03/15/2026` | 44-54 |
| NOTE_020 | **URL** | `https://clinical-portal.local/records/g-89211` | 60-105 |
| NOTE_020 | **DATE_TIME** | `4 weeks` | 273-280 |
| NOTE_020 | **PERSON** | `James Andrews` | 290-303 |
