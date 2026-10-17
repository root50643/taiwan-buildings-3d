"""Read-only normal/-O report parity after successful real CLI captures."""
from pathlib import Path
import json
import check_result_binding as binding


def main():
    base = Path(__file__).resolve().parent
    result = {'passed': True, 'comparisons': {}}
    for kind, key in [('controls', 'optimization_level'), ('binding', 'checker_optimization_level')]:
        documents = [binding.read(base / (kind + '-' + mode + '.json')) for mode in binding.MODES]
        binding.require(documents[0].pop(key) == 0 and documents[1].pop(key) == 1, 'Wrong actual report modes')
        binding.require(binding.exact(*documents), kind + ' reports differ outside allowed checker mode')
        result['comparisons'][kind] = {'identical_except': key, 'reports': {
            'checker/' + kind + '-' + mode + '.json': binding.record(base / (kind + '-' + mode + '.json')) for mode in binding.MODES}}
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
