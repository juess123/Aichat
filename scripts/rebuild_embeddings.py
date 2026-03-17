import sqlite3
import json
from model.embedding import encode
from config import DB_PATH

def rebuild_embeddings():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1️⃣ 读取所有数据
    cursor.execute("SELECT id, content FROM memories")
    rows = cursor.fetchall()

    print(f"🔍 共找到 {len(rows)} 条 memory，开始重建 embedding...")

    for i, (mid, content) in enumerate(rows):
        try:
            # 2️⃣ 重新编码
            emb = encode(content)
            print(len(emb))
            # 3️⃣ 转成 JSON 字符串（很重要！）
            emb_str = json.dumps(emb)

            # 4️⃣ 更新数据库
            cursor.execute(
                "UPDATE memories SET embedding = ? WHERE id = ?",
                (emb_str, mid)
            )
            
            if i % 10 == 0:
                print(f"✅ 已处理 {i}/{len(rows)}")

        except Exception as e:
            print(f"❌ id={mid} 出错: {e}")

    conn.commit()
    conn.close()

    print("🎉 embedding 重建完成！")

if __name__ == "__main__":
    rebuild_embeddings()