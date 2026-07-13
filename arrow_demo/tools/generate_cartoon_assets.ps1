Add-Type -AssemblyName System.Drawing

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$outDir = Join-Path $root "assets\textures"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

function New-Bitmap($width, $height, $transparent = $true) {
    $bmp = New-Object System.Drawing.Bitmap($width, $height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    if ($transparent) {
        $g.Clear([System.Drawing.Color]::Transparent)
    }
    return @{ Bitmap = $bmp; Graphics = $g }
}

function SolidBrush($hex) {
    return New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml($hex))
}

function Pen($hex, $width) {
    $p = New-Object System.Drawing.Pen([System.Drawing.ColorTranslator]::FromHtml($hex), $width)
    $p.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
    $p.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
    $p.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
    return $p
}

function Save-Png($asset, $fileName) {
    $path = Join-Path $outDir $fileName
    $asset.Graphics.Dispose()
    $asset.Bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $asset.Bitmap.Dispose()
    Write-Host $path
}

function Fill-RoundRect($g, $brush, $x, $y, $w, $h, $r) {
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $d = $r * 2
    $path.AddArc($x, $y, $d, $d, 180, 90)
    $path.AddArc($x + $w - $d, $y, $d, $d, 270, 90)
    $path.AddArc($x + $w - $d, $y + $h - $d, $d, $d, 0, 90)
    $path.AddArc($x, $y + $h - $d, $d, $d, 90, 90)
    $path.CloseFigure()
    $g.FillPath($brush, $path)
    $path.Dispose()
}

function Draw-Background {
    $asset = New-Bitmap 1280 720 $false
    $g = $asset.Graphics

    $skyRect = New-Object System.Drawing.Rectangle 0, 0, 1280, 500
    $sky = New-Object System.Drawing.Drawing2D.LinearGradientBrush($skyRect, [System.Drawing.ColorTranslator]::FromHtml("#8ed9ff"), [System.Drawing.ColorTranslator]::FromHtml("#f3fbff"), 90)
    $g.FillRectangle($sky, $skyRect)
    $sky.Dispose()

    $sun = SolidBrush "#ffe27a"
    $g.FillEllipse($sun, 1010, 60, 120, 120)
    $sun.Dispose()

    $cloud = SolidBrush "#ffffff"
    foreach ($c in @(
        @(120, 90, 82, 40), @(172, 74, 96, 58), @(240, 92, 78, 42),
        @(760, 120, 92, 46), @(826, 100, 110, 62), @(910, 124, 78, 42)
    )) {
        $g.FillEllipse($cloud, $c[0], $c[1], $c[2], $c[3])
    }
    $cloud.Dispose()

    $hillFar = SolidBrush "#91d68a"
    $hillNear = SolidBrush "#63bd6d"
    $g.FillEllipse($hillFar, -160, 310, 650, 260)
    $g.FillEllipse($hillFar, 410, 292, 720, 290)
    $g.FillEllipse($hillFar, 870, 305, 560, 250)
    $g.FillEllipse($hillNear, -260, 390, 820, 300)
    $g.FillEllipse($hillNear, 630, 386, 830, 320)
    $hillFar.Dispose()
    $hillNear.Dispose()

    $groundRect = New-Object System.Drawing.Rectangle 0, 470, 1280, 250
    $ground = New-Object System.Drawing.Drawing2D.LinearGradientBrush($groundRect, [System.Drawing.ColorTranslator]::FromHtml("#7bd962"), [System.Drawing.ColorTranslator]::FromHtml("#3aae57"), 90)
    $g.FillRectangle($ground, $groundRect)
    $ground.Dispose()

    $shadow = SolidBrush "#339a4c"
    $g.FillEllipse($shadow, 390, 535, 500, 76)
    $shadow.Dispose()

    $post = SolidBrush "#b77b39"
    $rail = SolidBrush "#d89a4c"
    for ($x = 45; $x -lt 1280; $x += 138) {
        Fill-RoundRect $g $post $x 410 30 110 10
    }
    Fill-RoundRect $g $rail 0 438 1280 24 8
    Fill-RoundRect $g $rail 0 482 1280 20 8
    $post.Dispose()
    $rail.Dispose()

    $grassA = Pen "#2c9447" 3
    $grassB = Pen "#a9f068" 3
    for ($i = 0; $i -lt 70; $i++) {
        $x = (37 * $i) % 1280
        $y = 600 + ((53 * $i) % 95)
        $g.DrawLine($grassA, $x, $y, $x + 8, $y - 18)
        if ($i % 2 -eq 0) {
            $g.DrawLine($grassB, $x + 8, $y, $x + 18, $y - 13)
        }
    }
    $grassA.Dispose()
    $grassB.Dispose()

    Save-Png $asset "cartoon_background.png"
}

function Draw-Sword {
    $asset = New-Bitmap 256 768 $true
    $g = $asset.Graphics

    $bladePath = New-Object System.Drawing.Drawing2D.GraphicsPath
    $bladePath.AddPolygon([System.Drawing.Point[]]@(
        [System.Drawing.Point]::new(128, 18),
        [System.Drawing.Point]::new(178, 505),
        [System.Drawing.Point]::new(128, 588),
        [System.Drawing.Point]::new(78, 505)
    ))
    $blade = New-Object System.Drawing.Drawing2D.LinearGradientBrush((New-Object System.Drawing.Rectangle 70, 18, 116, 570), [System.Drawing.ColorTranslator]::FromHtml("#f8fcff"), [System.Drawing.ColorTranslator]::FromHtml("#91b8ce"), 0)
    $g.FillPath($blade, $bladePath)
    $g.DrawPath((Pen "#4f7d95" 7), $bladePath)
    $blade.Dispose()
    $bladePath.Dispose()

    $shine = Pen "#ffffff" 7
    $g.DrawLine($shine, 124, 76, 108, 472)
    $shine.Dispose()

    $guard = SolidBrush "#f6b943"
    Fill-RoundRect $g $guard 50 555 156 38 18
    $g.DrawLine((Pen "#8a5b20" 6), 58, 574, 198, 574)
    $guard.Dispose()

    $handle = New-Object System.Drawing.Drawing2D.LinearGradientBrush((New-Object System.Drawing.Rectangle 98, 588, 60, 104), [System.Drawing.ColorTranslator]::FromHtml("#8a4f2b"), [System.Drawing.ColorTranslator]::FromHtml("#d88945"), 0)
    Fill-RoundRect $g $handle 98 586 60 118 22
    $handle.Dispose()
    $wrap = Pen "#5b3320" 8
    $g.DrawLine($wrap, 104, 610, 152, 632)
    $g.DrawLine($wrap, 152, 642, 104, 664)
    $g.DrawLine($wrap, 104, 676, 152, 698)
    $wrap.Dispose()

    $pommel = SolidBrush "#f3c34b"
    $g.FillEllipse($pommel, 92, 690, 72, 62)
    $g.DrawEllipse((Pen "#8a5b20" 6), 92, 690, 72, 62)
    $pommel.Dispose()

    Save-Png $asset "cartoon_sword.png"
}

function Draw-Wheel {
    $asset = New-Bitmap 512 512 $true
    $g = $asset.Graphics

    $cx = 256
    $cy = 256
    $rect = New-Object System.Drawing.Rectangle 36, 36, 440, 440
    $colors = @("#f45b69", "#ffd166", "#49c6e5", "#7dd87d", "#ff9f45", "#b388eb", "#4ecdc4", "#ff6f91")
    for ($i = 0; $i -lt 8; $i++) {
        $brush = SolidBrush $colors[$i]
        $g.FillPie($brush, $rect, -90 + ($i * 45), 45)
        $brush.Dispose()
    }

    $outline = Pen "#6b3f25" 18
    $g.DrawEllipse($outline, $rect)
    $outline.Dispose()

    $spoke = Pen "#f8e2b4" 8
    for ($i = 0; $i -lt 8; $i++) {
        $angle = (-90 + ($i * 45)) * [Math]::PI / 180.0
        $x = $cx + [Math]::Cos($angle) * 214
        $y = $cy + [Math]::Sin($angle) * 214
        $g.DrawLine($spoke, $cx, $cy, [int]$x, [int]$y)
    }
    $spoke.Dispose()

    $ring1 = Pen "#ffffff" 10
    $ring2 = Pen "#6b3f25" 8
    $g.DrawEllipse($ring1, 92, 92, 328, 328)
    $g.DrawEllipse($ring2, 146, 146, 220, 220)
    $ring1.Dispose()
    $ring2.Dispose()

    $center = SolidBrush "#fff3c4"
    $g.FillEllipse($center, 202, 202, 108, 108)
    $center.Dispose()
    $g.DrawEllipse((Pen "#6b3f25" 8), 202, 202, 108, 108)

    $pin = SolidBrush "#ff4d5e"
    $g.FillEllipse($pin, 232, 232, 48, 48)
    $pin.Dispose()

    $highlight = Pen "#ffffff" 7
    $g.DrawArc($highlight, 68, 62, 360, 360, 210, 70)
    $highlight.Dispose()

    Save-Png $asset "cartoon_wheel.png"
}

function Draw-PlayButton {
    $asset = New-Bitmap 256 256 $true
    $g = $asset.Graphics

    $shadow = SolidBrush "#00000033"
    $g.FillEllipse($shadow, 28, 34, 204, 204)
    $shadow.Dispose()

    $buttonRect = New-Object System.Drawing.Rectangle 24, 18, 208, 208
    $button = New-Object System.Drawing.Drawing2D.LinearGradientBrush($buttonRect, [System.Drawing.ColorTranslator]::FromHtml("#7df06f"), [System.Drawing.ColorTranslator]::FromHtml("#22b85a"), 90)
    $g.FillEllipse($button, $buttonRect)
    $button.Dispose()
    $g.DrawEllipse((Pen "#14783d" 10), $buttonRect)

    $shine = Pen "#dffff0" 11
    $g.DrawArc($shine, 55, 45, 120, 92, 210, 72)
    $shine.Dispose()

    $triPath = New-Object System.Drawing.Drawing2D.GraphicsPath
    $triPath.AddPolygon([System.Drawing.Point[]]@(
        [System.Drawing.Point]::new(104, 78),
        [System.Drawing.Point]::new(104, 178),
        [System.Drawing.Point]::new(178, 128)
    ))
    $triShadow = SolidBrush "#00000025"
    $matrix = New-Object System.Drawing.Drawing2D.Matrix
    $matrix.Translate(5, 6)
    $triPath.Transform($matrix)
    $g.FillPath($triShadow, $triPath)
    $matrix.Translate(-5, -6)
    $triPath.Transform($matrix)
    $triShadow.Dispose()
    $matrix.Dispose()

    $tri = SolidBrush "#ffffff"
    $g.FillPath($tri, $triPath)
    $g.DrawPath((Pen "#e4fff1" 5), $triPath)
    $tri.Dispose()
    $triPath.Dispose()

    Save-Png $asset "retry_play_button.png"
}

Draw-Background
Draw-Sword
Draw-Wheel
Draw-PlayButton
