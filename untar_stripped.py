#!/usr/bin/env python3

import argparse
import os.path
import struct
import sys
from datetime import datetime


class ArchiveItem:
    def __init__(self, header):
        self.name = header[0].decode()
        self.file_mode = header[1].decode()
        self.own_id = header[2].decode()
        self.group_id = header[3].decode()
        self.size = int(header[4].decode(), base=8)
        self.mod_time = datetime.utcfromtimestamp(int(header[5], base=8)).strftime('%d %b %Y %H:%M:%S')
        self.checksum = int(header[6].decode(), base=8)
        self.type = TarParser.FILE_TYPES[header[7]]
        self.linked_file_name = header[8].decode()
        self.user_name = header[11].decode()
        self.group_name = header[12].decode()
        self.content = str()

    def save_item_content(self, content_as_bytes):
        self.content = content_as_bytes.decode('ascii', errors='ignore')

    def get_item_info(self):
        return [
            ('Filename', self.name),
            ('Type', self.type),
            ('Mode', self.file_mode),
            ('UID', self.own_id),
            ('GID', self.group_id),
            ('Size', self.size),
            ('Modification time', self.mod_time),
            ('Checksum', self.checksum),
            ('User name', self.user_name),
            ('Group name', self.group_name),
        ]


class TarParser:
    _HEADER_FMT1 = '100s8s8s8s12s12s8sc100s255s'
    _HEADER_FMT2 = '6s2s32s32s8s8s155s12s'
    _HEADER_FMT3 = '6s2s32s32s8s8s12s12s112s31x'
    _READ_BLOCK = 16 * 2 ** 20

    FILE_TYPES = {
        b'0': 'Regular file',
        b'1': 'Hard link',
        b'2': 'Symbolic link',
        b'3': 'Character device node',
        b'4': 'Block device node',
        b'5': 'Directory',
        b'6': 'FIFO node',
        b'7': 'Reserved',
        b'D': 'Directory entry',
        b'K': 'Long linkname',
        b'L': 'Long pathname',
        b'M': 'Continue of last file',
        b'N': 'Rename/symlink command',
        b'S': "`sparse' regular file",
        b'V': "`name' is tape/volume header name"
    }

    def __init__(self, filename):
        """
        ?????????????????? tar-?????????? `filename' ?? ???????????????????? ?????? ??????????????????????????
        (???????? ??????????????????)
        """
        self.saved_items = {}
        self.extract_archive_items(filename)
        self.extract()

    def extract_archive_items(self, filename):
        """
        ?????????????? ?????????????????? ?????????????? (???????????????????? ?? ??????????) ???? ????????????
        """
        with open(filename, 'rb') as file:
            end = file.seek(0, os.SEEK_END)
            file.seek(0)
            while file.tell() <= self._READ_BLOCK and file.tell() < end:
                header = file.read(512)
                if header.startswith(b'\x00'):
                    continue
                else:
                    archive_item = self.create_archive_item(header)
                    archive_item.save_item_content(file.read(archive_item.size))
                    self.save_item(archive_item)
                    new_pointer = (512 - archive_item.size) % 512
                    file.seek(new_pointer, 1)

    def save_item(self, archive_item):
        """
        ?????????????? ?????????????????? ???????????????? ????????????
        """
        self.saved_items[archive_item.name] = archive_item

    def create_archive_item(self, header):
        """
        ?????????????? ?????????????? ???????????????? ????????????
        """
        header_first_half = struct.unpack(self._HEADER_FMT1, header)
        header_second_half = header_first_half[-1]
        if header_second_half.startswith(b'ustar\x00'):
            header_second_half = struct.unpack(self._HEADER_FMT2, header_second_half)
        else:
            header_second_half = struct.unpack(self._HEADER_FMT3, header_second_half)
        head = list(map(lambda x: x.replace(b'\x00', b''), header_first_half[:-1] + header_second_half))
        return ArchiveItem(head)

    def extract(self, dest=os.getcwd()):
        """
        ?????????????????????????? ???????????? tar-?????????? ?? ?????????????? `dest'
        """
        for archive_item in self.saved_items.values():
            if 'directory' in archive_item.type.lower():
                os.mkdir(os.path.join(dest, archive_item.name))
            else:
                file = open(os.path.join(dest, archive_item.name), 'w')
                file.write(archive_item.content)
                file.close()

    def files(self):
        """
        ???????????????????? ???????????????? ???????? ???????????? (?? ????????????) ?? ????????????
        """

        return iter(self.saved_items.keys())

    def file_stat(self, filename):
        """
        ???????????????????? ???????????????????? ?? ?????????? `filename' ?? ????????????.

        ???????????? (?????????????????? ???????? ?????????? ??????????????????????????, ?????????????????????? ????. ?? ????????????????
        ?????????????? tar):
        [
            ('Filename', '/NSimulator'),
            ('Type', 'Directory'),
            ('Mode', '0000755'),
            ('UID', '1000'),
            ('GID', '1000'),
            ('Size', '0'),
            ('Modification time', '29 Mar 2014 03:52:45'),
            ('Checksum', '5492'),
            ('User name', 'victor'),
            ('Group name', 'victor')
        ]
        """
        if filename not in self.files:
            raise ValueError(filename)

        info = [('Filename', filename)]

        info = self.saved_items[filename].get_item_info()
        return info


def print_file_info(stat, f=sys.stdout):
    max_width = max(map(lambda s: len(s[0]), stat))
    for field in stat:
        print("{{:>{}}} : {{}}".format(max_width).format(*field), file=f)


def main():
    parser = argparse.ArgumentParser(
        usage='{} [OPTIONS] FILE'.format(os.path.basename(sys.argv[0])),
        description='Tar extractor')
    parser.add_argument('-l', '--list', action='store_true', dest='ls',
                        help='list the contents of an archive')
    parser.add_argument('-x', '--extract', action='store_true', dest='extract',
                        help='extract files from an archive')
    parser.add_argument('-i', '--info', action='store_true', dest='info',
                        help='get information about files in an archive')
    parser.add_argument('fn', metavar='FILE',
                        help='name of an archive')

    args = parser.parse_args()
    if not (args.ls or args.extract or args.info):
        sys.exit("Error: action must be specified")

    try:
        tar = TarParser(args.fn)

        if args.info:
            for fn in sorted(tar.files()):
                print_file_info(tar.file_stat(fn))
                print()
        elif args.ls:
            for fn in sorted(tar.files()):
                print(fn)

        if args.extract:
            tar.extract()
    except Exception as e:
        sys.exit(e)


if __name__ == '__main__':
    main()
