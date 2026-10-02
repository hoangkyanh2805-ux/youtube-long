# SOP — THÊM CNAME `dashboard` TẠI iNET

**Mục đích:** trỏ `dashboard.azzamedu.com` → Cloudflare Pages (`azzam-reports.pages.dev`)
để team mở dashboard online, **không đụng** nameserver / email / site cũ.

**Thời gian:** ~3 phút thao tác + 5–30 phút chờ DNS.

**Trạng thái Cloudflare (đã xong):**
```
project : azzam-reports
domain  : dashboard.azzamedu.com
status  : pending
error   : "CNAME record not set"   ← chờ bước dưới
cert    : Google CA (tự cấp sau khi CNAME đúng)
```

---

## BƯỚC 0 — CHUẨN BỊ (đọc trước, 30 giây)

### Giá trị sẽ nhập

| Trường | Giá trị |
|--------|---------|
| Tên bản ghi (Name) | `dashboard` |
| Loại bản ghi (Type) | `CNAME` |
| Giá trị bản ghi (Value) | `azzam-reports.pages.dev` |
| TTL | `3600` (hoặc Auto / mặc định) |

**Lưu ý cách nhập tên:** iNET thường yêu cầu nhập **phần đầu** (không có `.azzamedu.com`).
Chỉ nhập `dashboard`. Nếu panel tự thêm domain đuôi thì để nguyên.
→ Nếu panel hiển thị preview `dashboard.azzamedu.com` là đúng.

### TUYỆT ĐỐI KHÔNG sửa/xoá những bản ghi sau

| Bản ghi | Giá trị | Nếu đụng vào |
|---------|---------|--------------|
| NS | `ns1.inet.vn`, `ns2.inet.vn`, `ns3.inet.vn` | Toàn bộ domain ngừng hoạt động |
| MX | `mx.zoho.com` (+ mx2, mx3) | **Email ngừng nhận thư** |
| A | `@` → `202.92.6.37` | **Website hiện tại sập** |
| A/CNAME | `www` → `202.92.6.37` | www sập |

Chỉ **THÊM MỚI**, không sửa cái đang có.

---

## BƯỚC 1 — ĐĂNG NHẬP iNET

1. Mở: **https://portal.inet.vn/**
2. Nhập email + mật khẩu tài khoản iNET của bạn
3. Nếu quên mật khẩu: bấm **Quên mật khẩu** để khôi phục

> Giao diện mới: `portal.inet.vn`
> Giao diện cũ (một số tài khoản): `inet.vn` → **Danh sách dịch vụ** → **Tên miền**

---

## BƯỚC 2 — VÀO QUẢN LÝ TÊN MIỀN

1. Trên menu chính, bấm **Tên miền** (hoặc **Domain**)
2. Danh sách tên miền hiện ra
3. **Tick vào ô chọn** cạnh `azzamedu.com`
4. Bấm nút **Bản ghi** (hoặc **Cập nhật bản ghi** / **DNS Records**)

> Mẹo: nếu không thấy nút, thử click trực tiếp vào tên `azzamedu.com` để mở chi tiết.

---

## BƯỚC 3 — XEM DANH SÁCH BẢN GHI HIỆN CÓ (quan trọng)

Trước khi thêm, **chụp màn hình lại** để có đường lùi. Bạn sẽ thấy các bản ghi:

```
@        A       202.92.6.37
www      A       202.92.6.37     (hoặc CNAME)
@        MX      mx.zoho.com
@        NS      ns1.inet.vn
...
```

**Kiểm tra:** có bản ghi nào tên `dashboard` chưa?
- **Chưa có** → sang Bước 4
- **Đã có** → xoá nó trước (nó đang chặn), rồi sang Bước 4

---

## BƯỚC 4 — THÊM BẢN GHI CNAME

1. Bấm **Thêm bản ghi** (hoặc **+ Add Record** / **Tạo mới bản ghi**)

2. Điền **đúng 4 trường**:

   | Trường trên form | Nhập gì |
   |------------------|---------|
   | **Tên bản ghi** / Record Name | `dashboard` |
   | **Loại** / Type | `CNAME` ← chọn từ dropdown |
   | **Giá trị** / Value / Target | `azzam-reports.pages.dev` |
   | **TTL** | `3600` hoặc để mặc định |

3. **Kiểm tra lại 2 điểm dễ sai nhất:**
   - Tên là `dashboard`, **KHÔNG PHẢI** `dashboard.azzamedu.com` (nếu panel tự thêm đuôi)
   - Giá trị **KHÔNG có** `https://` và **KHÔNG có** `/` ở cuối
     ```
     ✓ Đúng:  azzam-reports.pages.dev
     ✗ Sai:   https://azzam-reports.pages.dev/
     ✗ Sai:   azzam-reports.pages.dev/
     ```

4. Bấm **Tạo mới bản ghi** / **Save** / **Lưu**

5. Thấy thông báo thành công → bản ghi `dashboard CNAME azzam-reports.pages.dev` xuất hiện trong danh sách.

---

## BƯỚC 5 — CHỜ DNS (5–30 phút)

iNET ghi rõ: *"các bản ghi sẽ có hiệu lực trong nhiều nhất 30 phút"*.

Trong lúc chờ, kiểm tra bằng lệnh (mở CMD/PowerShell trên máy bạn):

```bash
nslookup dashboard.azzamedu.com 8.8.8.8
```

**Khi đã có hiệu lực**, kết quả sẽ hiện `Canonical name = azzam-reports.pages.dev`
và có địa chỉ IP của Cloudflare.

Chưa thấy → chờ thêm, hoặc kiểm tra lại Bước 4.

---

## BƯỚC 6 — XÁC NHẬN VỚI CLOUDFLARE

Sau khi DNS có hiệu lực, Cloudflare tự:
1. Xác minh domain (5–15 phút)
2. Cấp chứng chỉ HTTPS (Google CA, 5–15 phút)

**Kiểm tra trạng thái** — gửi tôi biết, tôi sẽ verify bằng API:
```
GET /accounts/<id>/pages/projects/azzam-reports/domains/dashboard.azzamedu.com
→ status: active  (là xong)
```

Hoặc bạn tự mở thử: **https://dashboard.azzamedu.com**

---

## NẾU GẶP LỖI

### Lỗi 1 — iNET báo "CNAME không hợp lệ" hoặc không cho lưu

Một số panel VN chặn CNAME trỏ ra ngoài domain. Thử theo thứ tự:

**a)** Đổi TTL về mặc định (Auto / 3600) rồi lưu lại

**b)** Thử nhập tên đầy đủ: `dashboard.azzamedu.com` (thay vì `dashboard`)

**c)** Nếu vẫn không được → **liên hệ iNET**:
- Ticket: https://helpdesk.inet.vn/ticket/my-ticket
- Hotline 24/7: **1900 9250**
- Nội dung: *"Tôi cần thêm bản ghi CNAME: tên `dashboard`, giá trị `azzam-reports.pages.dev`. Panel không cho lưu. Nhờ hỗ trợ thêm giúp."*

### Lỗi 2 — Sau 30 phút vẫn "CNAME record not set"

Kiểm tra bằng `nslookup`. Nếu vẫn không có CNAME:
- Chắc chắn đã bấm **Lưu** (nhiều panel không tự lưu)
- Kiểm tra lại đã tick đúng domain `azzamedu.com` chưa
- Thử đổi DNS resolver: `nslookup dashboard.azzamedu.com 1.1.1.1`

### Lỗi 3 — Site hiện tại bị ảnh hưởng

Nếu `azzamedu.com` hoặc `www` ngừng hoạt động → bạn đã sửa nhầm bản ghi `@` hoặc `www`.
**Khôi phục:** dùng ảnh chụp ở Bước 3, sửa lại đúng giá trị cũ (`202.92.6.37`).

### Lỗi 4 — HTTPS báo lỗi chứng chỉ

Bình thường trong 15 phút đầu. Cloudflare đang cấp cert. Chờ rồi thử lại.
Nếu sau 1 giờ vẫn lỗi → báo tôi.

---

## PHƯƠNG ÁN DỰ PHÒNG (nếu iNET không cho thêm CNAME)

Không cần domain vẫn dùng được — link Cloudflare Pages **đã cố định**:

```
https://azzam-reports.pages.dev
```

Link này **không đổi**, không phụ thuộc máy bạn, đã có HTTPS. Chỉ khác là không
đẹp bằng `dashboard.azzamedu.com`. Cứ gửi team link này nếu bước CNAME bế tắc.

---

## SAU KHI XONG

Gửi tôi biết, tôi sẽ:
1. Verify domain + cert qua Cloudflare API
2. Cập nhật link mới vào REPORT_HUB + Wiki dagu
3. Gửi link cho team qua Telegram (topic General + EDIT)

**Checklist hoàn thành:**
- [ ] Bước 1: đăng nhập portal.inet.vn
- [ ] Bước 2: vào Tên miền → chọn azzamedu.com → Bản ghi
- [ ] Bước 3: chụp ảnh danh sách bản ghi hiện có (để có đường lùi)
- [ ] Bước 4: thêm `dashboard CNAME azzam-reports.pages.dev`
- [ ] Bước 5: chờ 5–30 phút, kiểm tra bằng nslookup
- [ ] Bước 6: mở https://dashboard.azzamedu.com

---

*Nguồn hướng dẫn: helpdesk.inet.vn — "CNAME là gì? Ý nghĩa và cách sử dụng bản ghi CNAME"
và "Hướng dẫn trỏ tên miền về hosting chi tiết cho người mới".*
