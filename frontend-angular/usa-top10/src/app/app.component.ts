import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

export interface Destination {
  id: number;
  name: string;
  state: string;
  region: string;
  lat: number;
  lon: number;
  summary: string;
  best_time: string;
  tags: string;      // comma-separated in DB
  image: string;     // e.g., "newyorkcity.jpg"
  expanded?: boolean;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'Top 10 USA Vacation Destinations';
  destinations: Destination[] = [];
  message = '';
  isLoading = false;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadData();
  }

  /** Clean up filenames coming from the API (trim, remove inner spaces/newlines). */
  private cleanImageName(x: string): string {
    const s = (x || '').trim();
    // If your filenames never contain spaces, strip all spaces:
    return s.replace(/\s+/g, '');
  }

  /** Build the image src from a destination object. */
  imgSrc(d: Destination) {
    return `assets/images/${this.cleanImageName(d.image)}`;
  }

  /** Fallback chain: swap .jpg/.jpeg once, then use placeholder. */
  onImgError(event: Event) {
    const img = event.target as HTMLImageElement;
    const tried = img.getAttribute('data-tried') || '';
  
    // 1) Try swapping jpg <-> jpeg once
    if (!tried.includes('swap')) {
      img.setAttribute('data-tried', tried + ' swap');
      const lower = img.src.toLowerCase();
      if (lower.endsWith('.jpg')) { img.src = img.src.replace(/\.jpg$/i, '.jpeg'); return; }
      if (lower.endsWith('.jpeg')) { img.src = img.src.replace(/\.jpeg$/i, '.jpg'); return; }
    }
  
    // 2) Name-based fallback (e.g., "San Francisco" -> "sanfrancisco.jpg")
    const name = (img.dataset['name'] || '').toLowerCase();
    const slug = name.replace(/[^a-z0-9]+/g, ''); // strip spaces/punct
    if (slug) {
      img.src = `/assets/images/${slug}.jpg`;
      return;
    }
  
    // 3) Last resort: a neutral placeholder (optional)
    img.src = '/assets/images/placeholder.jpg';
  }

  tagsArray(d: Destination) {
    return (d.tags || '')
      .split(',')
      .map(t => t.trim())
      .filter(Boolean);
  }


  loadData() {
    this.http.get<{ destinations: Destination[] }>('http://127.0.0.1:8000/destinations')
      .subscribe({
  next: (res) => {
    const items = res?.destinations ?? [];
    this.destinations = items.map((d: any) => ({
      id: d.id,
      name: d.name,
      state: d.state,
      region: d.region,
      lat: d.lat,
      lon: d.lon,
      summary: d.short_desc,            // <— map here
      best_time: d.best_months,         // <— map here
      tags: d.tags,
      image: (d.hero_image || '').trim(), // <— map here
      expanded: false
    }));
  },
  error: (err) => console.error(err)
});
  }

  refreshData() {
    this.isLoading = true;
    this.message = 'Refreshing data...';
    this.http.get('http://127.0.0.1:8000/admin/refresh')
      .subscribe({
        next: () => {
          this.loadData();
          this.message = 'Data refreshed!';
          setTimeout(() => this.message = '', 1500);
        },
        error: (e) => {
          console.error(e);
          this.message = 'Failed to refresh.';
        }
      }).add(() => {
        this.isLoading = false;    
      });
  }
}