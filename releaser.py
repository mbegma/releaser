# -*- coding:utf-8 -*-
# -----------------------------------------------------
# Project Name: releaser
# Name: main
# Filename: releaser.py
# Author: mbegma
# Create data: 14.11.2025
# Description:
#
# Copyright: (c) mbegma, 2025
# History:
#        - 14.11.2025: start of development
# -----------------------------------------------------
import argparse
from pathlib import Path
import shutil
import zipfile
import tempfile
from datetime import datetime

# # Source - https://stackoverflow.com/a/36341469
# # Posted by Aaron Hall, modified by community. See post 'Timeline' for change history
# # Retrieved 2025-11-07, License - CC BY-SA 3.0
#
# from shutil import make_archive
# make_archive(
#   'zipfile_name',
#   'zip',           # the archive format - or tar, bztar, gztar
#   root_dir=None,   # root for archive - current working dir if None
#   base_dir=None)   # start archiving from here - cwd if None too


def _zip_directory(source_directory: Path, output_zip_file: Path) -> bool:
    """
    Zips a given directory into a specified ZIP file.
    Архивирует указанную директорию в указанный *.zip файл
    :param source_directory: (Path) The Path object of the directory to be zipped.
    :param output_zip_file: (Path) The Path object for the output ZIP file.
    :return: True or False
    """
    try:
        with zipfile.ZipFile(output_zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_directory.rglob('*'):
                if file_path.is_file():
                    zipf.write(file_path, arcname=file_path.relative_to(source_directory))
                elif file_path.is_dir():
                    # Add directories explicitly to ensure empty ones are included
                    zipf.write(file_path, arcname=file_path.relative_to(source_directory))
        print(f"Directory '{source_directory}' successfully zipped to '{output_zip_file}'.")
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def _create_files_object_list(source_dir: Path, extension_list: list, destination_dir: Path, excluded_dir: list) -> list:
    """
    Функция, которая формирует список с объектами-файлами, которые необходимо будет скопировать
    :param source_dir: Исходная директория с файлами
    :param extension_list: Список расширений фалов, которые необходимо скопировать ['.py', '.csv']
    :param destination_dir: Директория, куда нужно скопировать файлы
    :param excluded_dir: Список директорий, файлы из которых нужно исключить (включая саму директорию)
    :return: список объектов-файлов
    """
    _files_obj_list = []
    for extension in extension_list:
        print(f"process files with extension: {extension}")
        _files_generator = source_dir.rglob(f'*{extension}')
        _count = 0
        # находим разницу между списками parts у объектов source_dir и path_obj и это и будет неизменная часть,
        # ее добавляем к destination_dir и получаем полный путь, куда нужно скопировать файл
        for path_obj in _files_generator:
            _diff_list = [x for x in list(path_obj.parts) if x not in list(source_dir.parts)]
            # проверить, есть ли в _diff_list значения из _exclude_dir
            if len([x for x in _diff_list if x in excluded_dir]) == 0:
                _dest_path_obj = destination_dir.joinpath(*_diff_list)
                _files_obj_list.append({'from': path_obj, 'to': _dest_path_obj})
                print(f">> {path_obj} -> {_dest_path_obj}")
                _count += 1
            else:
                print(f"!! {path_obj} was excluded from processing")
        print(f"process files with extension: {extension} finished. Processed {_count} files.")
        print("-" * 30)
    return _files_obj_list

def _copy_files_object_list(files_object_list: list) -> int:
    """
    Функция копирует файлы по указанному пути
    :param files_object_list: список объектов у которых указано, что и куда копировать
    :return: количество скопированных объектов
    """
    _count = 0
    for _obj in files_object_list:
        if not _obj['to'].parent.exists():
            # если у файла отсутствует родительская директория, то создаем ее
            _obj['to'].parent.mkdir(parents=True, exist_ok=True)
        # копируем
        try:
            shutil.copy2(_obj['from'], _obj['to'])
            print(f">> {_obj['from']} -> {_obj['to']}")
            _count += 1
        except shutil.SameFileError:
            print("Source and destination are the same file.")
        except PermissionError:
            print("Permission denied when copying the file.")
        except Exception as e:
            print(f"An error occurred: {e}")
    return _count

def main():
    parser = argparse.ArgumentParser(description='Releaser tool')
    parser.add_argument('--dest_dir', type=str, help='Destination directory')
    parser.add_argument('--extensions', nargs='+', help='List of file extensions, like: py txt md')
    parser.add_argument('--excluded_dir', nargs='+', help='List of excluded directories, like: data, src')
    args = parser.parse_args()

    current_dir = Path.cwd() # текущая директория, откуда запущен скрипт
    print(f"current_dir: {current_dir}")

    source_dir = Path(__file__).parent.resolve() # директория, в которой находиться файл скрипта
    print(f"source_dir: {source_dir}")

    if args.dest_dir is None:
        print(f"Destination folder not specified")
        return

    destination_dir = Path(args.dest_dir) # директория назначения
    print(f"destination_dir: {destination_dir}")
    destination_dir.mkdir(parents=True, exist_ok=True)
    print(f"The folder '{destination_dir}' was created successfully or already exists.")

    if args.extensions is None:
        print(f"Extensions list not specified? set .*")
        args.extensions = ['.*']
    print(f"Processed extensions: {args.extensions}")

    if args.excluded_dir is None:
        args.excluded_dir = []
    print(f"Excluded folders: {args.excluded_dir}")

    _out_tmp_dir = tempfile.TemporaryDirectory(dir=destination_dir)
    print(f"tmp dir: {_out_tmp_dir.name}")

    _dest_list = _create_files_object_list(source_dir, args.extensions, Path(_out_tmp_dir.name), args.excluded_dir)
    _copy_files_count = _copy_files_object_list(_dest_list)
    print(f"copied {_copy_files_count} files from {len(_dest_list)} to {_out_tmp_dir.name}.")

    _zip_source_dir = Path(_out_tmp_dir.name)
    _output_zip_file = destination_dir / f"{current_dir.name}_{datetime.now():%Y-%m-%d_%H_%M_%S}.zip"
    if _zip_directory(_zip_source_dir, _output_zip_file):
        print(f"zipped {_output_zip_file}")
    else:
        print(f"failed to zip {_output_zip_file}")

    _out_tmp_dir.cleanup()

    print("finish")

if __name__ == '__main__':
    main()
