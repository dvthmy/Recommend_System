import pandas as pd
import glob
import os


def merge_recipetineats_csv(folder_path: str, output_filename: str = "vickypham_merged.csv"):
    """
    Merge all vickypham_*.csv files in a folder into one single CSV file.

    Args:
        folder_path (str): Path to the folder containing vickypham_.csv files.
        output_filename (str): Name of the merged output file (default: vickypham_merged.csv)
    """

    # 1️⃣ Tìm tất cả file CSV trong thư mục
    csv_files = sorted(glob.glob(os.path.join(folder_path, "vickypham_*.csv")))

    if not csv_files:
        print("⚠️ Không tìm thấy file nào có dạng vickypham_*.csv trong thư mục.")
        return


    # 2️⃣ Đọc và nối các file lại
    dfs = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            dfs.append(df)
            print(f"✅ Đã đọc: {os.path.basename(file)} ({len(df)} dòng)")
        except Exception as e:
            print(f"❌ Lỗi khi đọc {file}: {e}")

    merged_df = pd.concat(dfs, ignore_index=True)

    # 3️⃣ Lưu file hợp nhất
    output_path = os.path.join(r"D:\Recommend_System\pre_data", output_filename)
    merged_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"\n🎉 Hoàn tất! File đã được lưu tại:\n{output_path}")
    print(f"📊 Tổng số dòng sau khi gộp: {len(merged_df)}")


if __name__ == "__main__":
    # 🧭 Đường dẫn thư mục chứa các file vickypham_*.csv
    folder = r"D:\Recommend_System\pre_data\vickypham"  # 👉 đã sửa đúng đường dẫn

    # Test to verify the folder exists and has files
    print("Thư mục tồn tại:", os.path.exists(folder))

    files = glob.glob(os.path.join(folder, "*"))


    # Run the merge function
    merge_recipetineats_csv(folder)
