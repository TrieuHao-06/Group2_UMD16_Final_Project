
from supabase import create_client, Client

# 1. Thông tin kết nối dự án Supabase
SUPABASE_URL = "https://xdwecblyjvgsxvjdutkn.supabase.co"
SUPABASE_KEY = "sb_publishable_Zr-ACMtLAx464AE4h-Usgg_KPQfFlgi"

# 2. Khởi tạo Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Đã khởi tạo Supabase Client thành công!")
