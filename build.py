# -*- coding: utf-8 -*-
"""
sz-html 打包脚本

用途：生成 dist/sz-html-skill.zip，用于分发给用户直接安装。
说明：
  1. 49 风格资产随技能本地携带 → assets/ 必须入包；
  2. 构建产物输出到 Skill 包之外（.private/sz-html/dist/），严禁落在包内；
  3. 包内顶层目录固定为 sz-html/（安装后即该目录名）。
"""
import os
import sys
import zipfile

# 技能根目录（本脚本所在目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 产物目录：位于 Skill 包之外，避免产物被打进下一次构建
DIST_DIR = os.path.normpath(os.path.join(
    BASE_DIR, '..', '..', '..', '.private', 'sz-html', 'dist'))
# 包内顶层目录名
TOP_DIR = 'sz-html'
# 资产目录（随技能分发，故单独校验）
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

EXCLUDE_DIRS = {'.git', 'node_modules', 'dist', '__pycache__'}
EXCLUDE_PREFIX = ('_', '.')
EXCLUDE_EXT = {'.zip', '.log', '.tmp'}
EXCLUDE_FILES = {'build.py', 'build.bat'}


def fail(msg):
    print(f'[错误] {msg}')
    sys.exit(1)


def precheck():
    print('[1/3] 前置校验...')
    skill_md = os.path.join(BASE_DIR, 'SKILL.md')
    if not os.path.exists(skill_md):
        fail('缺少 SKILL.md，无法打包')
    if not os.path.exists(ASSETS_DIR):
        fail(f'缺少资产目录 {ASSETS_DIR}（资产必须随包）')
    asset_count = sum(len(files) for _, _, files in os.walk(ASSETS_DIR))
    if asset_count == 0:
        fail('资产目录为空，拒绝打包')
    print(f'  校验通过（资产 {asset_count} 个文件）')


def make_zip():
    print('[2/3] 打包...')
    os.makedirs(DIST_DIR, exist_ok=True)
    zip_path = os.path.join(DIST_DIR, 'sz-html-skill.zip')
    if os.path.exists(zip_path):
        os.remove(zip_path)
    added = []
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(BASE_DIR):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for name in files:
                if name in EXCLUDE_FILES or \
                        name.startswith(EXCLUDE_PREFIX) or \
                        os.path.splitext(name)[1].lower() in EXCLUDE_EXT:
                    continue
                fp = os.path.join(root, name)
                arcname = TOP_DIR + '/' + os.path.relpath(fp, BASE_DIR).replace('\\', '/')
                zf.write(fp, arcname)
                added.append(arcname)
    leaked = [a for a in added
              if a.endswith(('.pem', '.key', '.env', '.zip')) or 'deploy_config' in a]
    if leaked:
        fail(f'交付包内出现敏感文件，已中止: {leaked}')
    size = os.path.getsize(zip_path)
    print(f'  sz-html-skill.zip 大小: {size / 1024:.1f} KB，{len(added)} 个文件')
    return zip_path


def main():
    print('=' * 50)
    print('sz-html 打包')
    print('=' * 50)
    precheck()
    zip_path = make_zip()
    print('[3/3] 完成')
    print()
    print('=' * 50)
    print(f'打包完成: {zip_path}')
    print('解压后得到 sz-html/ 目录，放入 IDE 的技能目录即可')
    print('=' * 50)


if __name__ == '__main__':
    main()
