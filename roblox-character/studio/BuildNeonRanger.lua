--[[
	Neon Ranger - Roblox Studio character builder
	=============================================
	Dresses a rig with the Neon Ranger Shirt / Pants / Face and builds simple
	part-based stand-ins for the 3D accessories (hair, cat ears, Robin Hood cap,
	feather, halo, bow). Works on R6 and R15 block rigs.

	HOW TO USE (Roblox Studio on a Mac/PC):
	  1. Avatar tab > Rig Builder > "Block Rig" (R15) or R6 "Block Avatar".
	  2. Upload the three PNGs from the upload/ folder as images
	     (Home > Asset Manager / Toolbox > Import), then copy each image's ID.
	  3. Paste the IDs below.
	  4. Select the rig in the Explorer, then paste this whole file into
	     View > Command Bar and press Enter.

	Leave an ID at 0 to skip that item.
]]

local SHIRT_IMAGE_ID = 0 -- NeonRanger_Shirt_585x559.png
local PANTS_IMAGE_ID = 0 -- NeonRanger_Pants_585x559.png
local FACE_IMAGE_ID = 0 -- NeonRanger_Face_512.png

local SKIN = Color3.fromRGB(244, 226, 238)
local HAIR = Color3.fromRGB(34, 56, 178)
local HAIR_DARK = Color3.fromRGB(16, 24, 100)
local EAR_INNER = Color3.fromRGB(242, 124, 222)
local CLOAK = Color3.fromRGB(30, 74, 58)
local CLOAK_LIGHT = Color3.fromRGB(58, 116, 86)
local GOLD = Color3.fromRGB(214, 172, 82)
local NEON_GREEN = Color3.fromRGB(70, 255, 170)
local NEON_MAGENTA = Color3.fromRGB(255, 64, 226)
local FEATHER = Color3.fromRGB(222, 40, 162)
local BOW_WOOD = Color3.fromRGB(38, 32, 50)
local LEATHER = Color3.fromRGB(92, 56, 40)

local rig = game:GetService("Selection"):Get()[1]
if not (rig and rig:FindFirstChildOfClass("Humanoid")) then
	rig = workspace:FindFirstChild("Rig")
end
assert(rig and rig:FindFirstChildOfClass("Humanoid"), "Select a rig (Avatar > Rig Builder) before running")
local head = rig:FindFirstChild("Head")
local rightHand = rig:FindFirstChild("RightHand") or rig:FindFirstChild("Right Arm")

local function asset(id)
	return "rbxassetid://" .. tostring(id)
end

-- Clothing -------------------------------------------------------------------
for _, child in ipairs(rig:GetChildren()) do
	if child:IsA("Shirt") or child:IsA("Pants") or child:IsA("ShirtGraphic") or child.Name == "NeonRangerAccessories" then
		child:Destroy()
	end
end
if SHIRT_IMAGE_ID ~= 0 then
	local shirt = Instance.new("Shirt")
	shirt.ShirtTemplate = asset(SHIRT_IMAGE_ID)
	shirt.Parent = rig
end
if PANTS_IMAGE_ID ~= 0 then
	local pants = Instance.new("Pants")
	pants.PantsTemplate = asset(PANTS_IMAGE_ID)
	pants.Parent = rig
end

local bodyColors = rig:FindFirstChildOfClass("BodyColors") or Instance.new("BodyColors")
for _, prop in ipairs({ "HeadColor3", "TorsoColor3", "LeftArmColor3", "RightArmColor3", "LeftLegColor3", "RightLegColor3" }) do
	bodyColors[prop] = SKIN
end
bodyColors.Parent = rig

if FACE_IMAGE_ID ~= 0 then
	local old = head:FindFirstChild("face")
	if old then
		old:Destroy()
	end
	local face = Instance.new("Decal")
	face.Name = "face"
	face.Face = Enum.NormalId.Front
	face.Texture = asset(FACE_IMAGE_ID)
	face.Parent = head
end

-- Accessory helpers ----------------------------------------------------------
local model = Instance.new("Model")
model.Name = "NeonRangerAccessories"
model.Parent = rig

local function make(className, name, size, cframe, color, material, weldTo)
	local p = Instance.new(className)
	p.Name = name
	p.Size = size
	p.CFrame = cframe
	p.Color = color
	p.Material = material or Enum.Material.SmoothPlastic
	p.Anchored = false
	p.CanCollide = false
	p.CanQuery = false
	p.Massless = true
	p.CastShadow = false
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = model
	local weld = Instance.new("WeldConstraint")
	weld.Part0 = weldTo
	weld.Part1 = p
	weld.Parent = p
	return p
end

-- Part relative to the head. Offsets assume the standard ~1.2 stud block head;
-- the rig faces -Z, so negative Z is the front of the face.
local function onHead(className, name, size, offset, color, material)
	return make(className, name, size, head.CFrame * offset, color, material, head)
end

-- Thin rod between two points given in `base`'s local space.
local function rod(base, p0, p1, thickness, color, material, name)
	local a = base.CFrame:PointToWorldSpace(p0)
	local b = base.CFrame:PointToWorldSpace(p1)
	local size = Vector3.new(thickness, thickness, (b - a).Magnitude)
	return make("Part", name, size, CFrame.lookAt((a + b) / 2, b), color, material, base)
end

-- Hair: blue bob with bangs and side locks -----------------------------------
local cap = onHead("Part", "HairCap", Vector3.new(1.42, 0.8, 1.42), CFrame.new(0, 0.32, 0.04), HAIR)
Instance.new("SpecialMesh", cap).MeshType = Enum.MeshType.Sphere
onHead("Part", "HairBack", Vector3.new(1.38, 1.05, 0.34), CFrame.new(0, -0.08, 0.56), HAIR)
onHead("Part", "Bangs", Vector3.new(1.26, 0.2, 0.1), CFrame.new(0, 0.44, -0.63), HAIR)
for _, side in ipairs({ -1, 1 }) do
	onHead("Part", "SideLock", Vector3.new(0.18, 0.95, 0.42), CFrame.new(side * 0.67, -0.1, -0.2), HAIR_DARK)
end

-- Cat ears: triangles with a pink inner ------------------------------------------
for _, side in ipairs({ -1, 1 }) do
	local turn = CFrame.Angles(0, math.rad(-90 * side), math.rad(-12 * side))
	onHead("WedgePart", "CatEar", Vector3.new(0.1, 0.55, 0.42), CFrame.new(side * 0.5, 0.98, 0.1) * turn, HAIR)
	onHead("WedgePart", "CatEarInner", Vector3.new(0.1, 0.38, 0.28), CFrame.new(side * 0.5, 0.94, 0.04) * turn, EAR_INNER)
end

-- Robin Hood cap: brim, gold band, ridged crown, star badge, feather -----------
local upright = CFrame.Angles(0, 0, math.rad(90))
local brim = onHead("Part", "HatBrim", Vector3.new(0.14, 1.5, 1.5), CFrame.new(0, 0.62, 0) * upright, CLOAK_LIGHT)
brim.Shape = Enum.PartType.Cylinder
local band = onHead("Part", "HatBand", Vector3.new(0.05, 1.54, 1.54), CFrame.new(0, 0.7, 0) * upright, GOLD, Enum.Material.Metal)
band.Shape = Enum.PartType.Cylinder
for _, side in ipairs({ -1, 1 }) do
	onHead("WedgePart", "HatCrown", Vector3.new(1.35, 0.6, 0.62), CFrame.new(side * 0.31, 0.99, 0) * CFrame.Angles(0, math.rad(-90 * side), 0), CLOAK)
end
onHead("Part", "BadgeGold", Vector3.new(0.24, 0.24, 0.04), CFrame.new(-0.32, 0.74, -0.74) * CFrame.Angles(0, 0, math.rad(45)), GOLD, Enum.Material.Metal)
onHead("Part", "BadgeStar", Vector3.new(0.14, 0.14, 0.05), CFrame.new(-0.32, 0.74, -0.76) * CFrame.Angles(0, 0, math.rad(45)), NEON_GREEN, Enum.Material.Neon)
onHead("Part", "Feather", Vector3.new(0.05, 0.12, 1.1), CFrame.new(0.52, 1.02, 0.25) * CFrame.Angles(math.rad(35), math.rad(-15), 0), FEATHER)

-- Neon halo: ring of glowing segments -------------------------------------------
local SEGMENTS, RADIUS, HEIGHT = 28, 0.72, 1.5
local previous
for i = 0, SEGMENTS do
	local a = i / SEGMENTS * math.pi * 2
	local p = Vector3.new(math.cos(a) * RADIUS, HEIGHT, math.sin(a) * RADIUS)
	if previous then
		rod(head, previous, p, 0.07, NEON_MAGENTA, Enum.Material.Neon, "Halo")
	end
	previous = p
end
local light = Instance.new("PointLight")
light.Color = NEON_MAGENTA
light.Range = 6
light.Brightness = 1.5
light.Parent = model:FindFirstChild("Halo")

-- Bow in the right hand: dark limbs, neon green glyphs, glowing string ---------
if rightHand then
	local handDrop = rightHand.Name == "Right Arm" and -0.9 or 0
	local grip = Vector3.new(0, handDrop, -0.35)
	local tipTop = Vector3.new(0, handDrop + 1.5, -0.05)
	local tipBottom = Vector3.new(0, handDrop - 1.5, -0.05)
	local midTop = Vector3.new(0, handDrop + 0.8, -0.3)
	local midBottom = Vector3.new(0, handDrop - 0.8, -0.3)
	rod(rightHand, grip, midTop, 0.1, BOW_WOOD, nil, "BowLimb")
	rod(rightHand, midTop, tipTop, 0.08, BOW_WOOD, nil, "BowLimb")
	rod(rightHand, grip, midBottom, 0.1, BOW_WOOD, nil, "BowLimb")
	rod(rightHand, midBottom, tipBottom, 0.08, BOW_WOOD, nil, "BowLimb")
	rod(rightHand, grip + Vector3.new(0, -0.15, 0), grip + Vector3.new(0, 0.15, 0), 0.14, LEATHER, nil, "BowGrip")
	rod(rightHand, tipTop, tipBottom, 0.025, NEON_MAGENTA, Enum.Material.Neon, "BowString")
	for _, t in ipairs({ 0.4, 0.75 }) do
		for _, mid in ipairs({ midTop, midBottom }) do
			local p = grip:Lerp(mid, t) + Vector3.new(0, 0, -0.06)
			rod(rightHand, p - Vector3.new(0, 0.07, 0), p + Vector3.new(0, 0.07, 0), 0.04, NEON_GREEN, Enum.Material.Neon, "BowGlyph")
		end
	end
end

print("Neon Ranger built on " .. rig.Name)
