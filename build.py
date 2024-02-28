import sys
from pathlib import Path
from shutil import copy
from subprocess import call

import yaml
from pyinstaller_versionfile import MetaData, create_versionfile_from_input_file

root_path = Path(sys.argv[0]).parent


def yaml_read(path: Path):
    with open(str(path), 'r', encoding='utf-8') as fp:
        data = yaml.safe_load(fp)
    return data


def yaml_write(path: Path, data):
    with open(str(path), 'w') as fp:
        yaml.dump(data, fp, default_flow_style=False, encoding='utf-8')


class Builder:
    def __init__(self, build_path=None, name='main'):
        self.translations = [{'langID': 1033, 'charsetID': 1200}]
        self.metadata_file = root_path.joinpath(f'{name}_metadata.yml')
        self.__gen_metadata()
        self.build_dir = build_path or root_path.joinpath('build')
        self.build_dir.mkdir(exist_ok=True)

    def __gen_metadata(self):
        if not self.metadata_file.is_file():
            metadata = MetaData(
                version=input('version: '),
                company_name=input('company_name: '),
                file_description=input('file_description: '),
                internal_name=input('internal_name: '),
                legal_copyright=input('legal_copyright: '),
                original_filename=input('original_filename: '),
                product_name=input('product_name: '),
                translations=self.translations
            )
            yaml_write(self.metadata_file, metadata.to_dict())
        return self

    def __gen_version_file(self):
        create_versionfile_from_input_file(self.version_file.__str__(), self.metadata_file.__str__())
        return self

    @property
    def version_file(self):
        return self.build_dir.joinpath(f'{self.metadata.original_filename}.version')

    @property
    def metadata(self):
        return MetaData.from_file(self.metadata_file.__str__())

    @property
    def version_list(self):
        return [int(v) for v in self.metadata.version.split('.')]

    def upd_metadata(self, major=False, minor=False, micro=False):
        version = self.version_list
        major_ = version[0] + 1 if major else version[0]
        minor_ = 0 if major else version[1] + 1 if minor else version[1]
        micro_ = 0 if any([major, minor]) else version[2] + 1 if micro else version[2]
        build = 0 if any([major, minor, micro]) else version[3] + 1
        metadata = self.metadata
        metadata.set_version(f'{major_}.{minor_}.{micro_}.{build}')
        metadata.translations = self.translations
        yaml_write(self.metadata_file, metadata.to_dict())
        self.__gen_version_file()
        return self

    @classmethod
    def build(cls, command):
        print(command)
        call(command)

    def post(self):
        version = ".".join([str(i) for i in self.version_list])
        command = [
            'gh',
            'release',
            'create',
            f'v{version}',
            root_path.joinpath(f'dist\\{builder.metadata.original_filename}.exe').__str__()
        ]
        # call(command)
        print(' '.join(command))


if __name__ == '__main__':
    sys.path.append(root_path.joinpath('venv\\Scripts').__str__())
    builder = Builder()
    builder.upd_metadata(major=False, minor=False, micro=False)
    builder.build_dir.mkdir(exist_ok=True, parents=True)
    copy(root_path.joinpath('app.ico').__str__(), builder.build_dir.joinpath('app.ico').__str__())
    command_ = [
        'pyinstaller.exe',
        '--disable-windowed-traceback',
        '-F',
        '-w',
        '-a',
        '--clean',
        '-n',
        builder.metadata.original_filename,
        'test1.py',
        '--specpath',
        f'{builder.build_dir}',
        '--version-file',
        f'{builder.version_file.name}',
        '-i',
        f'app.ico',
        '--add-data',
        f'{root_path.joinpath("app.ico").__str__()};.'
    ]
    builder.build(command_)
    builder.post()
