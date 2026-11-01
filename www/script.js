// MEGATRON AI — High-Performance Holographic Particle Sphere
// Optimized with requestAnimationFrame & strictly bounded particle count for smooth 60FPS execution without memory leaks or UI freezes

window.addEventListener("load", windowLoadHandler, false);
var sphereRad = 140;
var radius_sp = 1;

function windowLoadHandler() {
    canvasApp();
}

function canvasSupport() {
    return !!(window.HTMLCanvasElement && document.createElement('canvas').getContext && document.createElement('canvas').getContext('2d'));
}

function canvasApp() {
    if (!canvasSupport()) {
        return;
    }

    var theCanvas = document.getElementById("canvasOne");
    if (!theCanvas) return;
    var context = theCanvas.getContext("2d");

    var displayWidth = theCanvas.width;
    var displayHeight = theCanvas.height;
    var animFrameId;
    var numToAddEachFrame = 2; // Lightweight addition
    var maxParticles = 180; // Strictly capped to prevent unbounded memory growth
    var currentParticleCount = 0;
    var particleList = { first: null };
    var recycleBin = { first: null };
    var particleAlpha = 1;
    var r = 0, g = 240, b = 255;
    var rgbString = "rgba(" + r + "," + g + "," + b + ",";
    var fLen = 320;
    var projCenterX = displayWidth / 2;
    var projCenterY = displayHeight / 2;
    var zMax = fLen - 2;
    var turnSpeed = 2 * Math.PI / 1600;
    var turnAngle = 0;
    var sphereCenterY = 0;
    var sphereCenterZ = -3 - sphereRad;
    var zeroAlphaDepth = -750;
    var particleRad = 1.7;
    var randAccelX = 0.08, randAccelY = 0.08, randAccelZ = 0.08;
    var gravity = 0;

    var lastTime = performance.now();

    function renderLoop(now) {
        animFrameId = requestAnimationFrame(renderLoop);

        // Throttle to max 60fps
        var elapsed = now - lastTime;
        if (elapsed < 15) return;
        lastTime = now;

        // Add new particles if under capacity
        if (currentParticleCount < maxParticles) {
            for (var i = 0; i < numToAddEachFrame; i++) {
                if (currentParticleCount >= maxParticles) break;
                var theta = Math.random() * 2 * Math.PI;
                var phi = Math.acos(Math.random() * 2 - 1);
                var x0 = sphereRad * Math.sin(phi) * Math.cos(theta);
                var y0 = sphereRad * Math.sin(phi) * Math.sin(theta);
                var z0 = sphereRad * Math.cos(phi);

                var p = addParticle(x0, sphereCenterY + y0, sphereCenterZ + z0, 0.002 * x0, 0.002 * y0, 0.002 * z0);
                p.attack = 40;
                p.hold = 40;
                p.decay = 80;
                p.initValue = 0;
                p.holdValue = particleAlpha;
                p.lastValue = 0;
                p.stuckTime = 80 + Math.random() * 20;
                p.accelX = 0;
                p.accelY = gravity;
                p.accelZ = 0;
            }
        }

        // Rotate sphere
        turnAngle = (turnAngle + turnSpeed) % (2 * Math.PI);
        var sinAngle = Math.sin(turnAngle);
        var cosAngle = Math.cos(turnAngle);

        // Clear canvas
        context.clearRect(0, 0, displayWidth, displayHeight);

        // Draw particles
        var p = particleList.first;
        var nextParticle;
        while (p != null) {
            nextParticle = p.next;
            p.age++;

            if (p.age > p.stuckTime) {
                p.velX += p.accelX + randAccelX * (Math.random() * 2 - 1);
                p.velY += p.accelY + randAccelY * (Math.random() * 2 - 1);
                p.velZ += p.accelZ + randAccelZ * (Math.random() * 2 - 1);
                p.x += p.velX;
                p.y += p.velY;
                p.z += p.velZ;
            }

            var rotX = cosAngle * p.x + sinAngle * (p.z - sphereCenterZ);
            var rotZ = -sinAngle * p.x + cosAngle * (p.z - sphereCenterZ) + sphereCenterZ;
            var m = radius_sp * fLen / (fLen - rotZ);
            p.projX = rotX * m + projCenterX;
            p.projY = p.y * m + projCenterY;

            if (p.age < p.attack + p.hold + p.decay) {
                if (p.age < p.attack) {
                    p.alpha = (p.holdValue - p.initValue) / p.attack * p.age + p.initValue;
                } else if (p.age < p.attack + p.hold) {
                    p.alpha = p.holdValue;
                } else {
                    p.alpha = (p.lastValue - p.holdValue) / p.decay * (p.age - p.attack - p.hold) + p.holdValue;
                }
            } else {
                p.dead = true;
            }

            var outsideTest = (p.projX > displayWidth) || (p.projX < 0) || (p.projY < 0) || (p.projY > displayHeight) || (rotZ > zMax);

            if (outsideTest || p.dead) {
                recycle(p);
            } else {
                var depthAlphaFactor = (1 - rotZ / zeroAlphaDepth);
                depthAlphaFactor = (depthAlphaFactor > 1) ? 1 : ((depthAlphaFactor < 0) ? 0 : depthAlphaFactor);
                context.fillStyle = rgbString + Math.max(0, Math.min(1, depthAlphaFactor * p.alpha)) + ")";

                context.beginPath();
                context.arc(p.projX, p.projY, Math.max(0.5, m * particleRad), 0, 2 * Math.PI, false);
                context.closePath();
                context.fill();
            }

            p = nextParticle;
        }
    }

    function addParticle(x0, y0, z0, vx0, vy0, vz0) {
        var newParticle;
        if (recycleBin.first != null) {
            newParticle = recycleBin.first;
            if (newParticle.next != null) {
                recycleBin.first = newParticle.next;
                newParticle.next.prev = null;
            } else {
                recycleBin.first = null;
            }
        } else {
            newParticle = {};
        }

        if (particleList.first == null) {
            particleList.first = newParticle;
            newParticle.prev = null;
            newParticle.next = null;
        } else {
            newParticle.next = particleList.first;
            particleList.first.prev = newParticle;
            particleList.first = newParticle;
            newParticle.prev = null;
        }

        newParticle.x = x0;
        newParticle.y = y0;
        newParticle.z = z0;
        newParticle.velX = vx0;
        newParticle.velY = vy0;
        newParticle.velZ = vz0;
        newParticle.age = 0;
        newParticle.dead = false;
        currentParticleCount++;
        return newParticle;
    }

    function recycle(p) {
        if (particleList.first == p) {
            if (p.next != null) {
                p.next.prev = null;
                particleList.first = p.next;
            } else {
                particleList.first = null;
            }
        } else {
            if (p.next == null) {
                if (p.prev) p.prev.next = null;
            } else {
                if (p.prev) p.prev.next = p.next;
                p.next.prev = p.prev;
            }
        }

        if (recycleBin.first == null) {
            recycleBin.first = p;
            p.prev = null;
            p.next = null;
        } else {
            p.next = recycleBin.first;
            recycleBin.first.prev = p;
            recycleBin.first = p;
            p.prev = null;
        }
        currentParticleCount = Math.max(0, currentParticleCount - 1);
    }

    // Start 60FPS animation loop
    animFrameId = requestAnimationFrame(renderLoop);
}