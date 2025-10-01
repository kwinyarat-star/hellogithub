# app2.py
from flask import Flask, request, render_template_string, redirect, url_for

# 1. ตั้งค่า Flask App
app = Flask(__name__)
# Secret key สำหรับความปลอดภัย (จำเป็นสำหรับ session หรือ flash messages)
app.secret_key = "supersecretkey" 

# 2. จำลองฐานข้อมูล (ใช้ List of Dictionaries เก็บในหน่วยความจำ)
# ในโปรแกรมจริงควรใช้ฐานข้อมูลเช่น SQLite, PostgreSQL
products = [
    {'id': 1, 'name': 'Monitor Dell 24"', 'description': 'IPS Panel, 144Hz', 'price': 7500, 'quantity': 15},
    {'id': 2, 'name': 'Mechanical Keyboard', 'description': 'Keychron K8, Brown Switch', 'price': 3400, 'quantity': 8}
]
# ตัวแปรสำหรับ ID ถัดไป เพื่อไม่ให้ ID ซ้ำกัน
next_id = 3

# 3. สร้างเทมเพลต HTML ทั้งหมดในตัวแปรเดียว
# เราใช้ render_template_string เพื่อให้ทุกอย่างอยู่ในไฟล์เดียว
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ระบบบันทึกข้อมูลอุปกรณ์คอมพิวเตอร์</title>
    <style>
        body { font-family: 'Sarabun', sans-serif; background-color: #f4f4f9; color: #333; margin: 20px; }
        .container { max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1, h2 { color: #0056b3; text-align: center; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background-color: #007bff; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .actions a { margin-right: 10px; text-decoration: none; color: #007bff; }
        .actions a.delete { color: #dc3545; }
        form { margin-top: 20px; padding: 20px; border: 1px solid #ccc; border-radius: 8px; background: #fafafa; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="number"] { width: 95%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
        button {
            background-color: #28a745; color: white; padding: 10px 20px; border: none;
            border-radius: 4px; cursor: pointer; font-size: 16px;
        }
        button.update { background-color: #ffc107; color: black; }
        .form-title { font-size: 1.5em; margin-bottom: 20px; color: #333; }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1>ระบบบันทึกข้อมูลอุปกรณ์คอมพิวเตอร์</h1>

        <!-- ฟอร์มสำหรับ เพิ่ม และ แก้ไข ข้อมูล -->
        <!-- เราใช้ Logic ของ Jinja2 เพื่อเปลี่ยนการทำงานของฟอร์ม -->
        <form action="{{ url_for('update', product_id=product_to_edit.id) if product_to_edit else url_for('add') }}" method="post">
            <div class="form-title">
                {% if product_to_edit %}
                    แก้ไขข้อมูลสินค้า (ID: {{ product_to_edit.id }})
                {% else %}
                    เพิ่มข้อมูลสินค้าใหม่
                {% endif %}
            </div>
            <div class="form-group">
                <label for="name">ชื่อสินค้า:</label>
                <input type="text" id="name" name="name" value="{{ product_to_edit.name if product_to_edit else '' }}" required>
            </div>
            <div class="form-group">
                <label for="description">รายละเอียด:</label>
                <input type="text" id="description" name="description" value="{{ product_to_edit.description if product_to_edit else '' }}">
            </div>
            <div class="form-group">
                <label for="price">ราคา:</label>
                <input type="number" id="price" name="price" step="0.01" value="{{ product_to_edit.price if product_to_edit else '' }}" required>
            </div>
            <div class="form-group">
                <label for="quantity">จำนวน:</label>
                <input type="number" id="quantity" name="quantity" value="{{ product_to_edit.quantity if product_to_edit else '' }}" required>
            </div>
            {% if product_to_edit %}
                <button type="submit" class="update">อัปเดตข้อมูล</button>
                <a href="{{ url_for('index') }}" style="margin-left: 10px;">ยกเลิกการแก้ไข</a>
            {% else %}
                <button type="submit">บันทึกข้อมูล</button>
            {% endif %}
        </form>

        <h2>รายการอุปกรณ์ทั้งหมด</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>ชื่อสินค้า</th>
                    <th>รายละเอียด</th>
                    <th>ราคา</th>
                    <th>จำนวน</th>
                    <th>จัดการ</th>
                </tr>
            </thead>
            <tbody>
                {% for product in products %}
                <tr>
                    <td>{{ product.id }}</td>
                    <td>{{ product.name }}</td>
                    <td>{{ product.description }}</td>
                    <td>{{ "%.2f"|format(product.price) }}</td>
                    <td>{{ product.quantity }}</td>
                    <td class="actions">
                        <a href="{{ url_for('index', product_id=product.id) }}">แก้ไข</a>
                        <a href="{{ url_for('delete', product_id=product.id) }}" class="delete" onclick="return confirm('คุณแน่ใจหรือไม่ที่จะลบข้อมูลนี้?')">ลบ</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

# 4. สร้าง Routes (เส้นทางของเว็บ)

# หน้าหลัก (แสดงฟอร์มและตาราง) และหน้าแก้ไข
@app.route('/')
@app.route('/edit/<int:product_id>')
def index(product_id=None):
    product_to_edit = None
    if product_id:
        # ค้นหาสินค้าที่ต้องการแก้ไขจาก list
        product_to_edit = next((p for p in products if p['id'] == product_id), None)
    
    # ส่งข้อมูลทั้งหมดและข้อมูลที่ต้องการแก้ไข (ถ้ามี) ไปยังเทมเพลต
    return render_template_string(HTML_TEMPLATE, products=products, product_to_edit=product_to_edit)

# Route สำหรับเพิ่มข้อมูล (รับค่าจากฟอร์มแบบ POST)
@app.route('/add', methods=['POST'])
def add():
    global next_id
    # ดึงข้อมูลจากฟอร์มที่ส่งมา
    name = request.form['name']
    description = request.form['description']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])

    # สร้าง Dictionary ของสินค้าใหม่
    new_product = {
        'id': next_id,
        'name': name,
        'description': description,
        'price': price,
        'quantity': quantity
    }
    products.append(new_product)
    next_id += 1 # เพิ่มค่า ID สำหรับรายการถัดไป

    return redirect(url_for('index')) # กลับไปยังหน้าหลัก

# Route สำหรับอัปเดตข้อมูล
@app.route('/update/<int:product_id>', methods=['POST'])
def update(product_id):
    # ค้นหาสินค้าที่ต้องการอัปเดต
    product_to_update = next((p for p in products if p['id'] == product_id), None)
    if product_to_update:
        # อัปเดตข้อมูลจากฟอร์ม
        product_to_update['name'] = request.form['name']
        product_to_update['description'] = request.form['description']
        product_to_update['price'] = float(request.form['price'])
        product_to_update['quantity'] = int(request.form['quantity'])
    
    return redirect(url_for('index'))

# Route สำหรับลบข้อมูล
@app.route('/delete/<int:product_id>')
def delete(product_id):
    global products
    # กรอง list เพื่อเอาสินค้าที่ต้องการลบออก
    products = [p for p in products if p['id'] != product_id]
    
    return redirect(url_for('index'))

# 5. สั่งให้แอปพลิเคชันทำงาน
if __name__ == '__main__':
    # debug=True ทำให้เว็บเซิร์ฟเวอร์รีสตาร์ทเองเมื่อมีการแก้โค้ด และแสดงข้อผิดพลาดละเอียด
    app.run(debug=True, port=5001)