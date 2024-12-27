from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/data', methods=['POST'])
def get_data():
    response = {
        "data": [
            {
                "image": "/uploads/3a2085697544492897827f2b79b467d8.jpg",
                "list": []
            },
            {
                "image": "/uploads/3a2085697544492897827f2b79b467d8.jpg",
                "list": [
                    [
                        {"confidence": 0.8706732136862618, "is_match": True, "text": "20IT525"},
                        {"confidence": 0.5341371297836304, "is_match": True, "text": "9.0"}
                    ],
                    [
                        {"confidence": 0.8653437580381121, "is_match": False, "text": "20IT523"},
                        {"confidence": 0.9439283013343811, "is_match": False, "text": "8.0"}
                    ],
                    [
                        {"confidence": 0.8701872485024589, "is_match": True, "text": "20IT526"},
                        {"confidence": 0.9443634748458862, "is_match": True, "text": "8.0"}
                    ],
                    [
                        {"confidence": 0.8514404211725507, "is_match": True, "text": "20ITO19"},
                        {"confidence": 0.8602124651273092, "is_match": True, "text": "8.5"}
                    ],
                    [
                        {"confidence": 0.865754212651934, "is_match": True, "text": "201TO44"},
                        {"confidence": 0.9368823170661926, "is_match": True, "text": "8.5"}
                    ]
                ]
            },
            {
                "image": "/uploads/3a2085697544492897827f2b79b467d8.jpg",
                "list": [
                    [
                        {"confidence": 0.861218912260873, "is_match": True, "text": "201TO45"},
                        {"confidence": 0.9353104035059611, "is_match": True, "text": "8.5"}
                    ],
                    [
                        {"confidence": 0.8505350947380066, "is_match": True, "text": "20ITO36"},
                        {"confidence": 0.8918696045875549, "is_match": True, "text": "8.5"}
                    ],
                    [
                        {"confidence": 0.899759658745357, "is_match": True, "text": "20IT545"},
                        {"confidence": 0.9403746128082275, "is_match": True, "text": "8.0"}
                    ],
                    [
                        {"confidence": 0.8590753333909171, "is_match": False, "text": "20ITO16"},
                        {"confidence": 0.9418060183525085, "is_match": False, "text": "8.0"}
                    ],
                    [
                        {"confidence": 0.8990090233939034, "is_match": True, "text": "20IT235"},
                        {"confidence": 0.9369900822639465, "is_match": True, "text": "9.0"}
                    ],
                    [
                        {"confidence": 0.8630632076944623, "is_match": True, "text": "20IT236"},
                        {"confidence": 0.9368756214777628, "is_match": True, "text": "8.5"}
                    ]
                ]
            }
        ],
        "title_results": [
            [
                {"confidence": 0.93353686820377, "coordinates": [114, 80, 376, 107], "ocr_text": "KHOA KHOA HỌC MÁY TÍNH"},
                {"confidence": 0.9295258935954835, "coordinates": [189, 206, 484, 233], "ocr_text": "Đồ án chuyên ngành 3 - Hội đồng 3-SE"},
                {"confidence": 0.9294968975914849, "coordinates": [43, 181, 272, 209], "ocr_text": "Học kỳ 2, Năm học 2023-2024"}
            ],
            [],
            []
        ]
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
    # endpoint :  http://127.0.0.1:5000/api/data
