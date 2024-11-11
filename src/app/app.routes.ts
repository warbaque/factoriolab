import { PreloadAllModules, RouterModule, Routes } from '@angular/router';

import { canActivateLanding } from './guards';

export const routes: Routes = [
  {
    path: 'wizard',
    loadComponent: () =>
      import('./routes/wizard/wizard.component').then((c) => c.WizardComponent),
  },
  {
    path: '',
    pathMatch: 'full',
    canActivate: [canActivateLanding],
    loadComponent: () =>
      import('./routes/landing/landing.component').then(
        (c) => c.LandingComponent,
      ),
  },
  {
    path: '',
    loadChildren: () =>
      import('./routes/main/main.module').then((m) => m.MainModule),
  },
  {
    path: 'factorio',
    redirectTo: '/?s=&v=9',
  },
  {
    path: 'coi',
    redirectTo: '/?s=coi&v=9',
  },
  {
    path: 'dsp',
    redirectTo: '/?s=dsp&v=9',
  },
  {
    path: 'satisfactory',
    redirectTo: '/?s=sfy&v=9',
  },
  {
    path: 'techtonica',
    redirectTo: '/?s=tta&v=9',
  },
  {
    path: 'final-factory',
    redirectTo: '/?s=ffy&v=9',
  },
  {
    path: 'minecraft-statech-industry',
    redirectTo: '/?s=mcsi&v=9',
  },
  {
    path: 'minecraft-modern-industrialization',
    redirectTo: '/?s=mcmi&v=9',
  },
  {
    path: '**',
    redirectTo: '',
  },
];

export const AppRoutingModule = RouterModule.forRoot(routes, {
  preloadingStrategy: PreloadAllModules,
  paramsInheritanceStrategy: 'always',
});
