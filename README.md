# releaser
Tools for release some code &amp; files   

Идея инструмента в том, что бы при запуске он взял все файлы заданных расширений из папки в которой он запущен, 
убрал файлы, находящиеся в папках, указанных как исключения и создал структурированный архив с файлами (релиз), 
который можно передавать при необходимости.     
Все настройки через параметры запуска в *.bat файле.
   
## Шаблон для *.bat файла    
<путь к python.exe>  releaser.py --dest_dir <папка в которой доложен быть создан архив> --extensions <перечень расширений> --excluded_dir <перечень папок>
  
#### Пример:     
C:\Python\Python312\python.exe releaser.py --dest_dir d:\releases\project_x --extensions .py .ini .md --excluded_dir data json-files _tmp 
