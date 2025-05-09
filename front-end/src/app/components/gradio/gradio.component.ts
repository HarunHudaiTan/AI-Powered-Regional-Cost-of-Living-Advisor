import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-gradio',
  template: '',
  standalone: true
})
export class GradioComponent implements OnInit {
  ngOnInit() {
    window.location.href = 'http://127.0.0.1:7860';
  }
} 