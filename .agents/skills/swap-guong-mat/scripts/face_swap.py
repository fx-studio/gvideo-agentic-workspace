#!/usr/bin/env python3
"""Run an external FaceFusion 3.9.0 installation without uploading media."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime


def nonnegative(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError('Phải >= 0')
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', nargs='+', required=True, type=Path)
    parser.add_argument('--target', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--facefusion-dir', type=Path, default=os.environ.get('FACEFUSION_DIR'))
    parser.add_argument('--python', default=os.environ.get('FACEFUSION_PYTHON', sys.executable))
    parser.add_argument('--model', default='hyperswap_1a_256')
    parser.add_argument('--enhancer-blend', type=int, choices=range(101), default=30, metavar='0..100')
    parser.add_argument('--provider', choices=['cpu', 'cuda', 'coreml', 'directml'], default='cpu')
    parser.add_argument('--face-position', type=nonnegative, default=0)
    parser.add_argument('--reference-frame', type=nonnegative, default=0)
    parser.add_argument('--reference-distance', type=float, choices=[i / 20 for i in range(21)], default=0.3)
    parser.add_argument('--face-order', choices=['left-right', 'right-left', 'large-small', 'small-large'], default='left-right')
    parser.add_argument('--thu', '--dry-run', action='store_true', dest='dry_run')
    args = parser.parse_args(argv)
    if not args.facefusion_dir:
        parser.error('Cần --facefusion-dir hoặc FACEFUSION_DIR; xem SKILL.md để cài FaceFusion 3.9.0')
    ff = args.facefusion_dir.expanduser().resolve()
    sources = [path.expanduser().resolve() for path in args.source]
    target = args.target.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not (ff / 'facefusion.py').is_file():
        parser.error('Không tìm thấy facefusion.py trong --facefusion-dir')
    for path in sources + [target]:
        if not path.is_file():
            parser.error(f'Không tìm thấy đầu vào: {path}')
    if any(path.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp', '.bmp'} for path in sources):
        parser.error('--source phải là ảnh, mỗi ảnh chỉ chứa một người')
    if output in sources + [target] or output.exists():
        parser.error('Đầu ra đã tồn tại hoặc trùng đầu vào; chọn đường dẫn mới')
    video = target.suffix.lower() in {'.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v'}
    if not video and target.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}:
        parser.error('Định dạng target không được hỗ trợ')
    if output.suffix.lower() not in ({'.mp4'} if video else {'.png', '.jpg', '.jpeg', '.webp'}):
        parser.error('Video xuất .mp4; ảnh xuất .png/.jpg/.jpeg/.webp')
    python = shutil.which(args.python)
    if not python:
        parser.error('Không tìm thấy Python của môi trường FaceFusion')
    command = [python, str(ff / 'facefusion.py'), 'headless-run',
               '--source-paths', *map(str, sources), '--target-path', str(target),
               '--output-path', str(output), '--processors', 'face_swapper']
    if args.enhancer_blend:
        command += ['face_enhancer']
    command += ['--face-swapper-model', args.model, '--face-selector-mode', 'reference',
                '--face-selector-order', args.face_order,
                '--reference-face-position', str(args.face_position),
                '--reference-frame-number', str(args.reference_frame),
                '--reference-face-distance', str(args.reference_distance),
                '--face-mask-types', 'box', 'occlusion', '--execution-providers', args.provider,
                '--output-image-quality', '100', '--output-image-scale', '1.0',
                '--output-video-quality', '95', '--output-video-scale', '1.0',
                '--output-video-encoder', 'libx264', '--output-video-preset', 'slow']
    if args.enhancer_blend:
        command += ['--face-enhancer-model', 'gfpgan_1.4', '--face-enhancer-blend', str(args.enhancer_blend)]
    # Do not override output-video-fps: retain the source's frame rate.
    print(json.dumps({'cwd': str(ff), 'command': command, 'dry_run': args.dry_run}, ensure_ascii=False, indent=2))
    if args.dry_run:
        return 0
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        parser.error('Cần ffmpeg và ffprobe trên PATH')
    output.parent.mkdir(parents=True, exist_ok=True)
    run_dir = output.parent / (datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '_swap-guong-mat')
    run_dir.mkdir()
    metadata = {'command': command, 'cwd': str(ff), 'source': list(map(str, sources)),
                'target': str(target), 'output': str(output), 'status': 'running'}
    try:
        with (run_dir / 'facefusion.log').open('w', encoding='utf-8') as log:
            result = subprocess.run(command, cwd=ff, stdout=log, stderr=subprocess.STDOUT, check=False)
        success = result.returncode == 0 and output.is_file() and output.stat().st_size > 0
        metadata.update(status='success' if success else 'failed', returncode=result.returncode)
    except (OSError, KeyboardInterrupt) as error:
        metadata.update(status='failed', error=str(error))
        success = False
    (run_dir / 'RUN.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"{'Hoàn tất' if success else 'Thất bại'}: {output}\nLog: {run_dir}")
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
