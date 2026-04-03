<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lumen: Neural Architecture</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js"></script>
  <style>
    :root { --accent: #00ffcc; --bg: #020305; }
    body { margin: 0; background: var(--bg); color: white; font-family: monospace; overflow: hidden; }
    #ui { position: fixed; left: 40px; top: 50%; transform: translateY(-50%); z-index: 100; pointer-events: none; }
    #news-text { font-size: 22px; max-width: 450px; font-weight: bold; text-transform: uppercase; margin-bottom: 20px; transition: all 0.8s ease; letter-spacing: 1px; line-height: 1.3; }
    .label { color: var(--accent); letter-spacing: 3px; font-size: 10px; margin-bottom: 5px; opacity: 0.6; }
    .stat { margin-bottom: 20px; }
    #score { font-size: 18px; font-weight: bold; }
    #debug-log { position: fixed; bottom: 10px; left: 10px; font-size: 8px; color: #333; pointer-events: none; }
    canvas { display: block; }
  </style>
</head>
<body>
  <div id="ui">
    <div class="stat">
      <div class="label">NEURAL_FEED_STATUS</div>
      <div id="status">INIT_SEQUENCING...</div>
    </div>
    <div id="news-text">CONNECTING_TO_STREAM...</div>
    <div class="stat">
      <div class="label">SENTIMENT_ANALYSIS</div>
      <div id="score">0.00</div>
    </div>
  </div>
  <div id="debug-log">LOG: System start...</div>

  <script>
    let newsData = [];
    let currentIndex = 0;
    let angle = 0;
    let particles = [];
    
    // Legacy Design Tokens
    const petalCounts = [4, 6, 10, 12, 16, 2, 80]; 
    const anatomicalY = [380, 260, 120, 0, -140, -260, -360];
    const chakraColors = [
      [255, 50, 50], [255, 105, 180], [255, 215, 0], 
      [0, 255, 120], [0, 180, 255], [176, 191, 26], [200, 80, 255]
    ];

    function log(msg) {
      console.log(msg);
      document.getElementById('debug-log').innerText = "LOG: " + msg;
    }

    async function loadNews() {
      const statusEl = document.getElementById('status');
      const repoName = window.location.pathname.split('/')[1];
      const path = window.location.hostname.includes('github.io') ? `/${repoName}/data/news.json` : 'data/news.json';

      try {
        const response = await fetch(`${path}?t=${Date.now()}`);
        if (response.ok) {
          newsData = await response.json();
          statusEl.innerText = "SIGNAL_STABLE";
          log("Data synced.");
          updateDisplay();
        } else { throw new Error(); }
      } catch (e) {
        log("External feed failed. Using simulated backup.");
        statusEl.innerText = "SIMULATED_FEED";
        newsData = [{"text": "NEURAL CORE STABILIZED", "score": 5.0, "color_hex": "#00ffcc"}];
        updateDisplay();
      }
    }

    function updateDisplay() {
      if (newsData.length === 0) return;
      const item = newsData[currentIndex];
      document.getElementById('news-text').innerText = item.text;
      document.getElementById('score').innerText = item.score;
      if (item.color_hex) document.documentElement.style.setProperty('--accent', item.color_hex);
      
      setTimeout(() => {
        currentIndex = (currentIndex + 1) % newsData.length;
        updateDisplay();
      }, 10000);
    }

    function setup() {
      createCanvas(windowWidth, windowHeight, WEBGL);
      setAttributes('antialias', true);
      for(let i=0; i<80; i++) {
        particles.push({
          pos: createVector(random(-800, 800), random(-800, 800), random(-800, 800)),
          speed: random(0.001, 0.005)
        });
      }
      loadNews();
    }

    function draw() {
      background(10, 12, 20); // Darker legacy background
      orbitControl(1, 1, 0.1);
      
      let score = parseFloat(newsData[currentIndex]?.score || 0);
      let intensity = map(score, -15, 15, 0.1, 1.2);
      
      // Floating Starfield
      let accentCol = getComputedStyle(document.documentElement).getPropertyValue('--accent');
      stroke(accentCol);
      strokeWeight(1.5);
      beginShape(POINTS);
      particles.forEach(p => {
        let x = p.pos.x * sin(frameCount * p.speed);
        let y = p.pos.y * cos(frameCount * p.speed);
        vertex(x, y, p.pos.z);
      });
      endShape();

      // The Anatomical Chakra Design
      translate(0, 0, -200); 

      for (let i = 0; i < 7; i++) {
        push();
        translate(0, anatomicalY[i], 0);

        let phase = frameCount * 0.01 + (i * 0.8);
        let pulse = sin(phase);
        let petals = petalCounts[i];
        let c = chakraColors[i];

        // Rotation logic from legacy
        rotateY(frameCount * 0.005 + (i * 0.12));
        rotateX(sin(phase * 0.3) * 0.12);

        // Petal Layers
        noFill();
        for (let j = 0; j < 3; j++) {
          push();
          let baseRadius = 55 + (j * 15);
          stroke(c[0], c[1], c[2], 180 - (j * 40));
          strokeWeight(1.4 + (intensity * 2.5));

          beginShape();
          for (let a = 0; a < TWO_PI; a += 0.05) {
            let petalShape = sin(a * petals) * (7 + intensity * 25);
            let noiseOff = noise(cos(a) + i, sin(a) + j, frameCount * 0.005);
            let wobble = map(noiseOff, 0, 1, -5, 5) * (1 + intensity * 7);
            
            let r = baseRadius + petalShape + (pulse * 5) + wobble;
            let x = r * cos(a);
            let y = r * sin(a);
            let z = cos(phase + a) * (6 + intensity * 20);
            vertex(x, y, z);
          }
          endShape(CLOSE);
          pop();
        }

        // Inner Yantra Symbols
        push();
        fill(c[0], c[1], c[2], 80 + (intensity * 40));
        noStroke();
        rotateZ(frameCount * 0.012);
        let sz = 24 + (pulse * 4);

        if (i === 0) box(sz);
        else if (i === 1) { rotateZ(HALF_PI); arc(0, 0, sz * 1.6, sz * 1.6, 0, PI); }
        else if (i === 2) drawYantraTriangle(sz, true);
        else if (i === 3) { drawYantraTriangle(sz, true); drawYantraTriangle(sz, false); }
        else if (i === 4) { ellipse(0, 0, sz * 1.2, sz * 1.2, 40); fill(255, 120); drawYantraTriangle(sz * 0.6, true); }
        else if (i === 5) drawYantraTriangle(sz, true);
        else if (i === 6) sphere(sz * 0.9, 24, 24);
        pop();

        pop();
      }
      angle += 0.01;
    }

    function drawYantraTriangle(size, inverted) {
      beginShape();
      let m = inverted ? 1 : -1;
      vertex(0, 1 * size * m);
      vertex(-0.86 * size, -0.5 * size * m);
      vertex(0.86 * size, -0.5 * size * m);
      endShape(CLOSE);
    }

    function windowResized() { resizeCanvas(windowWidth, windowHeight); }
  </script>
</body>
</html>
