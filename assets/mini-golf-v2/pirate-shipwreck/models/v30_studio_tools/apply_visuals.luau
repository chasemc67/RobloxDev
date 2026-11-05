assert(game.PlaceId==131316561222931)
local ship=workspace.World.StartShip
local raw=game.ServerStorage.StartShipImport.v3_2.start_ship_b2_visual
local retired=Instance.new("Folder"); retired.Name="v30_PreviousVisuals"; retired.Parent=game.ServerStorage.StartShipImport
local G=CFrame.new(-690,0.6,160)*CFrame.Angles(0,math.rad(102),0)
local r={}
for _,d in {{n="DeckCabin",c=Vector3.new(-11.929496765136719,27.350000381469727,20.26949977874756)},{n="Hull",c=Vector3.new(20.280494689941406,36.28750133514404,13.720499038696289)},{n="Prop_Barnacles",c=Vector3.new(37.82350158691406,11.096999540925026,17.664000511169434)},{n="Prop_BowRaise",c=Vector3.new(104.25,46.73849868774414,12.030499458312988)},{n="Prop_BulwarkFrames",c=Vector3.new(13.177001953125,42.17700004577637,11.881999969482422)},{n="Prop_BulwarkGear",c=Vector3.new(-63.3544979095459,37.38100051879883,12.930000305175781)},{n="Prop_CabinWindows",c=Vector3.new(-115.38349914550781,33.2185001373291,8.14799976348877)},{n="Prop_Cannons",c=Vector3.new(-35.0049991607666,28.015000343322754,13.24000072479248)},{n="Prop_CapRails",c=Vector3.new(20.6405029296875,50.347999572753906,13.653999328613281)},{n="Prop_CargoCluster",c=Vector3.new(-100.25450134277344,27.75,29.459999084472656)},{n="Prop_Crab",c=Vector3.new(-95.12950134277344,33.97249984741211,27.828999519348145)},{n="Prop_DoorLantern",c=Vector3.new(-107.5,35.07499885559082,26)},{n="Prop_DoorLantern_Glow",c=Vector3.new(-107.5,34,26.899999618530273)},{n="Prop_Figurehead",c=Vector3.new(165.52850341796875,41.50250053405762,10.330499649047852)},{n="Prop_Flag",c=Vector3.new(95.55299758911133,117.3910026550293,28.616498947143555)},{n="Prop_PatchPlanks",c=Vector3.new(9.000499725341797,12.272500276565552,4.990499496459961)},{n="Prop_Portholes",c=Vector3.new(-43.22200012207031,37.81750011444092,23.135499835014343)},{n="Prop_RoofTrim",c=Vector3.new(-120,47.808000564575195,2.5)},{n="Prop_RopeCoils",c=Vector3.new(20.5675048828125,27.65999984741211,19.94899994134903)},{n="Prop_Seaweed",c=Vector3.new(31.807998657226562,29.033500909805298,15.192000389099121)},{n="Prop_SheerWale",c=Vector3.new(-0.5684967041015625,42.22350025177002,10.955499649047852)},{n="Prop_SternCastle",c=Vector3.new(-139.01000213623047,61.05900192260742,16.19600009918213)},{n="Prop_SternCurl",c=Vector3.new(-165.7415008544922,49.619001388549805,16.385501861572266)},{n="Prop_SternWheel",c=Vector3.new(-68.93600082397461,31.285500526428223,30.5)},{n="Prop_Stovepipe",c=Vector3.new(-138.38599395751953,54.2189998626709,13.871999740600586)},{n="Prop_TreasureChest",c=Vector3.new(-79.98200225830078,28.341500282287598,38.645498275756836)},{n="Rigging",c=Vector3.new(22.840499877929688,64.22350001335144,11.712499618530273)}} do
 local source=assert(raw:FindFirstChild(d.n))
 local old=ship:FindFirstChild(d.n)
 if old then old.Parent=retired end
 local p=source:Clone()
 p.CFrame=G*CFrame.new(d.c)*CFrame.Angles(0,math.pi,0)
 p.PivotOffset=CFrame.new()
 p.Anchored=true p.CanCollide=false p.CanQuery=false p.CanTouch=false
 p.TextureID="rbxassetid://127118214115521" p.Color=Color3.new(1,1,1) p.Material=Enum.Material.Plastic
 if d.n:find("Glow") then p.Material=Enum.Material.Neon p.CastShadow=false end
 p:SetAttribute("V30","start_ship_b2_detail_v3_2") p:SetAttribute("MeshAsset",p.MeshId)
 p.Parent=ship
 r[d.n]={id=p.MeshId,size={p.Size.X,p.Size.Y,p.Size.Z}}
end
return game:GetService("HttpService"):JSONEncode(r)
