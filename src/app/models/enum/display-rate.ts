import { SelectItem } from 'primeng/api';

import { Rational, rational } from '../rational';

export enum DisplayRate {
  PerTick = 1,
  PerSecond = 20 * 1,
  PerMinute = 20 * 60,
  PerHour = 20 * 3600,
}

export const displayRateOptions: SelectItem<DisplayRate>[] = [
  { value: DisplayRate.PerTick, label: 'options.displayRate.perTick' },
  { value: DisplayRate.PerSecond, label: 'options.displayRate.perSecond' },
  { value: DisplayRate.PerMinute, label: 'options.displayRate.perMinute' },
  { value: DisplayRate.PerHour, label: 'options.displayRate.perHour' },
];

export interface DisplayRateInfo {
  option: DisplayRate;
  suffix: string;
  itemsLabel: string;
  wagonsLabel: string;
  pollutionLabel: string;
  value: Rational;
}

export const displayRateInfo: Record<DisplayRate, DisplayRateInfo> = {
  [DisplayRate.PerTick]: {
    option: DisplayRate.PerTick,
    suffix: 'options.displayRate.perTickSuffix',
    itemsLabel: 'options.objectiveUnit.itemsPerTick',
    wagonsLabel: 'options.objectiveUnit.wagonsPerTick',
    pollutionLabel: 'options.objectiveUnit.pollutionPerTick',
    value: rational(DisplayRate.PerTick),
  },
  [DisplayRate.PerSecond]: {
    option: DisplayRate.PerSecond,
    suffix: 'options.displayRate.perSecondSuffix',
    itemsLabel: 'options.objectiveUnit.itemsPerSecond',
    wagonsLabel: 'options.objectiveUnit.wagonsPerSecond',
    pollutionLabel: 'options.objectiveUnit.pollutionPerSecond',
    value: rational(DisplayRate.PerSecond),
  },
  [DisplayRate.PerMinute]: {
    option: DisplayRate.PerMinute,
    suffix: 'options.displayRate.perMinuteSuffix',
    itemsLabel: 'options.objectiveUnit.itemsPerMinute',
    wagonsLabel: 'options.objectiveUnit.wagonsPerMinute',
    pollutionLabel: 'options.objectiveUnit.pollutionPerMinute',
    value: rational(DisplayRate.PerMinute),
  },
  [DisplayRate.PerHour]: {
    option: DisplayRate.PerHour,
    suffix: 'options.displayRate.perHourSuffix',
    itemsLabel: 'options.objectiveUnit.itemsPerHour',
    wagonsLabel: 'options.objectiveUnit.wagonsPerHour',
    pollutionLabel: 'options.objectiveUnit.pollutionPerHour',
    value: rational(DisplayRate.PerHour),
  },
};
