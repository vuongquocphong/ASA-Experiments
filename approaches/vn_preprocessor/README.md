Công cụ tiền xử lý
===============================

Yêu cầu
---------------------;
**python 3.6 trở lên**
Nếu trên máy có cài các phiên bản python khác thì phải bảo đảm các lệnh trong hướng dẫn được chạy bằng python 3.6 trở lên.
Một số máy có cài đặt python 2.x, sau khi cài thêm python 3.6 thì lệnh có thể là python3 hoặc python36... Trong hướng dẫn sẽ sử dụng lệnh python (giả sử máy chỉ cài python 3.6).

Hướng dẫn sử dụng
----------------------;
Mở Command Prompt tại thư mục chứa source code.

**Tiền xử lý**:
Chạy lệnh:

```bash
python preprocess.py <Đường dẫn đến file hoặc thư mục input> <Đường dẫn đến file hoặc thư mục output> [Thêm -ow nếu muốn ghi đè output, mặc định sẽ báo lỗi nếu file đã tồn tại]
```

Ví dụ:

```bash
python preprocess.py D:/tmp/inp.txt D:/tmp/out.txt
python preprocess.py D:/tmp/inp.txt D:/tmp/out.txt -ow
```

**Tách câu**:
Chạy lệnh (yêu cầu câu đã được tiền xử lý từ trước):

```bash
python sentence_segment.py <Đường dẫn đến file hoặc thư mục input> <Đường dẫn đến file hoặc thư mục output> [Thêm -ow nếu muốn ghi đè output, mặc định sẽ báo lỗi nếu file đã tồn tại]
```

Ví dụ:

```bash
python sentence_segment.py D:/tmp/inp.txt D:/tmp/out.txt
python sentence_segment.py D:/tmp/inp.txt D:/tmp/out.txt -ow
```

===============================
Hướng dẫn sử dụng cho dev
----------------------;
Import và khai báo:

```python
from preprocessor import *
# Khai báo đối tượng preprocessor cho tiếng Việt.
# Khi khai báo, các file liên quan sẽ được nạp vào bộ nhớ.
p = Preprocessor(Language.vietnamese)
```

Hàm **preprocess**:
Tiền xử lý một câu.

Tham số:

* sentence (str): Câu để tiền xử lý.
* replace_y_i (bool): Thay thế y bằng i. Mặc định là False.

Ví dụ lệnh:

```python
# Không thay thế y bằng i
p.preprocess('Tôi ăn cơm')
# Có thay thế y bằng i
p.preprocess('Tôi sang Nhật vào quý 4', True)
```

---------------------------;
Hàm **preprocess_list**:
Tiền xử lý danh sách các câu

Tham số:

* sentences (list): Danh sách các câu để tiền xử lý.
* replace_y_i (bool): Thay thế y bằng i. Mặc định là False.

Ví dụ lệnh:

```python
# Truyền trực tiếp
p.preprocess(['Tôi ăn cơm', 'Tôi uống nước'])
# Khai báo danh sách trước
l = [
    'Tôi ăn cơm',
    'Tôi uống nước'
    ]
p.preprocess(l)
```

---------------------------;
Hàm **preprocess_files**:
Tiền xử lý một hay nhiều file. Mỗi file xuất chứa một hoặc nhiều câu, mỗi câu nằm trên một dòng.

* inp_path (str): Đường dẫn đến file chứa danh sách các câu hoặc thư mục chứa nhiều file.
* out_path (str): Đường dẫn đến file xuất hoặc thư mục muốn xuất.
* options (dict): Các tuỳ chọn
    overwrite (bool): Nếu True thì ghi đè file khi file đã tồn tại,
                        ngược lại, văng lỗi FileExistsError.
                        Giá trị mặc định là False.
    replace_y_i (bool): Nếu True thì thay thế y bằng i.
                        Giá trị mặc định là False.

Ví dụ lệnh:

```python
# Đọc vào file inp.txt, các câu tiền xử lý lưu vào file out.txt.
# Nếu file out.txt đã tồn tại thì báo lỗi.
# Không thay thế y bằng i
p.preprocess_files('D:/tmp/inp.txt', 'D:/tmp/out.txt')
# Đọc vào file inp.txt, các câu tiền xử lý lưu vào file out.txt.
# Nếu file out.txt đã tồn tại thì ghi đè.
# Không thay thế y bằng i
p.preprocess_files('D:/tmp/inp.txt', 'D:/tmp/out.txt', {'overwrite': True})
```

---------------------------;
Hàm **segment_to_sentences**:
Tách câu

Tham số:

* text (str): Input text.
* preprocess (bool): Nếu True thì tiền xử lý trước khi tách câu.
                    Mặc định là False.
* replace_y_i (bool): Chỉ có hiệu lực khi tham số preprocess là True.
                    Nếu True thì thay thế y bằng i.
                    Mặc định là False.

Ví dụ lệnh:

```python
# Tách câu không tiền xử lý
p.segment_to_sentences('Tôi ăn cơm. Tôi uống nước')
# Tách câu và tiền xử lý, không thay thế y bằng i.
p.segment_to_sentences('Tôi ăn cơm. Tôi uống nước', True)
# Tách câu và tiền xử lý, thay thế y bằng i.
p.segment_to_sentences('Tôi ăn cơm. Tôi uống nước', True, True)
```

---------------------------;
Hàm **segment_files_to_sentences**:
Tách câu

Tham số:

* inp_path (str): Đường dẫn đến file chứa danh sách các câu hoặc thư mục chứa nhiều file.
* out_path (str): Đường dẫn đến file xuất hoặc thư mục muốn xuất.
* options (dict): Các tuỳ chọn
    overwrite (bool): Nếu True thì ghi đè file khi file đã tồn tại,
                        ngược lại, văng lỗi FileExistsError.
                        Giá trị mặc định là False.
    preprocess (bool): Nếu True thì tiền xử lý trước khi tách câu.
                        Mặc định là False.
    replace_y_i (bool): Chỉ có hiệu lực khi tuỳ chọn preprocess là True.
                        Nếu True thì thay thế y bằng i.
                        Giá trị mặc định là False.

Ví dụ lệnh:

```python
# Đọc vào file inp.txt, tách câu không tiền xử lý lưu vào file out.txt.
# Nếu file out.txt đã tồn tại thì báo lỗi.
p.segment_files_to_sentences('D:/tmp/inp.txt', 'D:/tmp/out.txt')
# Đọc vào file inp.txt, tách câu không tiền xử lý lưu vào file out.txt.
# Nếu file out.txt đã tồn tại thì ghi đè.
p.segment_files_to_sentences('D:/tmp/inp.txt', 'D:/tmp/out.txt', {'overwrite': True})
# Đọc vào file inp.txt, tiền xử lý rồi tách câu lưu vào file out.txt.
# Không thay thế y bằng i.
# Nếu file out.txt đã tồn tại thì báo lỗi.
p.segment_files_to_sentences('D:/tmp/inp.txt', 'D:/tmp/out.txt', {'preprocess': True})
# Đọc vào tất cả file trong thư mục D:/inp, tiền xử lý rồi tách câu lưu vào các file trong thư mục D:/out.
# Không thay thế y bằng i.
# Nếu file trong thư mục D:/out đã tồn tại thì báo lỗi.
# Tên file xuất giống tên file gốc.
p.segment_files_to_sentences('D:/inp', 'D:/out', {'preprocess': True})
```
