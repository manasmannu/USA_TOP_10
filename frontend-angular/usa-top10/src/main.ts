import 'zone.js'; 
// src/main.ts
import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient } from '@angular/common/http';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, {
  providers: [provideHttpClient()],
}).catch(err => console.error(err));


// import { bootstrapApplication } from '@angular/platform-browser';
// import { provideHttpClient, withFetch } from '@angular/common/http';
// import { AppComponent } from './app/app.component';

// bootstrapApplication(AppComponent, {
//   providers: [provideHttpClient(withFetch())]
// });