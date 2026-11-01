"""Recalculate every numerical PWM example. No hardware measurements."""
import json
import math
from pathlib import Path

F_TIM = 72_000_000
MAX16 = 65_535

def config(psc, arr, ccr, v_high=3.3):
    assert 0 <= psc <= MAX16 and 1 <= arr <= MAX16
    assert 0 <= ccr <= MAX16
    tick_hz = F_TIM / (psc + 1)
    duty = min(ccr / (arr + 1), 1.0)
    return dict(psc=psc, arr=arr, ccr=ccr, tick_hz=tick_hz,
                frequency_hz=tick_hz / (arr + 1),
                period_us=1e6 * (arr + 1) / tick_hz,
                high_us=1e6 * min(ccr, arr + 1) / tick_hz,
                duty_percent=100 * duty, ideal_mean_v=v_high * duty,
                duty_step_percentage_points=100 / (arr + 1),
                resolution_bits=math.log2(arr + 1))

def best_exact(frequency_hz):
    # A smaller divider maximizes ARR at the same exact output frequency.
    for divider in range(1, 65_537):
        counts, remainder = divmod(F_TIM, divider * frequency_hz)
        if not remainder and 2 <= counts <= MAX16 + 1:
            return dict(psc=divider-1, arr=counts-1,
                        counts=counts, bits=math.log2(counts))
    raise ValueError('No exact 16-bit configuration')

result = dict(clock_hz=F_TIM,
              nominal_examples=[config(71, 999, c) for c in (250, 500, 750)],
              best_exact_1khz=best_exact(1000),
              best_exact_20khz=best_exact(20000),
              invalid_1khz_psc0_arr=F_TIM//1000-1,
              endpoint_100percent=config(71,999,1000),
              ccr65536_fits_16bit=(65536<=MAX16),
              timer_input_tick_ns=1e9/F_TIM,
              counter_tick_us=(71+1)*1e6/F_TIM,
              example_exact_10hz=config(143,49999,25000),
              max_16bit_duty_percent=100*65535/65536,
              gamma_lut_32=[round(1000*(k/31)**2.2) for k in range(32)])
assert result['best_exact_1khz']['psc'] == 1
assert result['best_exact_1khz']['arr'] == 35999
assert result['best_exact_20khz']['arr'] == 3599
assert [x['high_us'] for x in result['nominal_examples']] == [250,500,750]
assert result['invalid_1khz_psc0_arr'] > MAX16
assert result['endpoint_100percent']['duty_percent'] == 100
assert not result['ccr65536_fits_16bit']
out = Path(__file__).with_name('calculations.json')
out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(out.read_text(encoding='utf-8'))
