# GuardNet-AI — Pedoman Anotasi Final

## Tujuan
Memberikan label ground truth secara independen sebelum evaluasi model.

## Kelas
- C0 — Non-Gambling: konten tidak mempromosikan perjudian dan tidak berfokus pada aktivitas perjudian sebagai objek promosi.
- C1 — Gambling-Related Non-Promotion: berita, edukasi, penelitian, kampanye anti-judi, atau pembahasan perjudian tanpa tujuan promosi.
- C2 — Gambling Promotion: konten yang menawarkan, mengajak, mengarahkan, atau memfasilitasi akses terhadap perjudian online.

## Aturan
1. Annotator 1 dan Annotator 2 bekerja secara independen.
2. Jangan melihat prediksi GuardNet-AI ketika memberi label.
3. Jika ragu, tuliskan alasan di notes/rekam keputusan adjudication.
4. Jika A1 != A2, jangan memilih label berdasarkan prediksi model.
5. Lakukan adjudication dan isi final_label setelah disagreement diselesaikan.
6. Simpan identitas sensitif dalam bentuk masked/pseudonymized jika tidak diperlukan untuk eksperimen.
7. Ground truth final hanya berasal dari proses anotasi manusia + adjudication.

## Unit analisis
Satu content unit Instagram dapat berupa post, Reel, carousel, atau komentar publik relevan. Modalitas yang tersedia untuk unit yang sama digabungkan di bawah Sample ID.
