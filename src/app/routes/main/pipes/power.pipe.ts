import { Pipe, PipeTransform } from '@angular/core';

import { PowerUnit, Rational, rational } from '~/models';
import { RatePipe } from './rate.pipe';

@Pipe({ name: 'power' })
export class PowerPipe implements PipeTransform {
  transform(
    value: Rational,
    precision: number | null,
    unit?: PowerUnit,
  ): string {
    switch (unit) {
      case PowerUnit.GW:
        return `${RatePipe.transform(
          value.div(rational(1000000n)),
          precision,
        )} MEU/t`;
      case PowerUnit.MW:
        return `${RatePipe.transform(
          value.div(rational(1000n)),
          precision,
        )} kEU/t`;
      default:
        return `${RatePipe.transform(value, precision)} EU/t`;
    }
  }
}
