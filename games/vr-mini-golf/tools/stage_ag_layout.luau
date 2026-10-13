local me=game.Players.LocalPlayer
local card
for _, root in {me.PlayerGui,workspace.CurrentCamera} do
 for _, d in root:GetDescendants() do
  if d:IsA("Frame") and d.Name=="Scorecard" then card=d break end
 end
end
assert(card,"scorecard is not open")
local function bounds(o)
 return {x=o.AbsolutePosition.X,y=o.AbsolutePosition.Y,w=o.AbsoluteSize.X,h=o.AbsoluteSize.Y}
end
local function overlap(a,b)
 return math.max(0,math.min(a.x+a.w,b.x+b.w)-math.max(a.x,b.x))*math.max(0,math.min(a.y+a.h,b.y+b.h)-math.max(a.y,b.y))
end
local a,b,c=bounds(card.Title),bounds(card.Close),bounds(card.SettingsButton)
return game.HttpService:JSONEncode({title=a,close=b,gear=c,titleClose=overlap(a,b),titleGear=overlap(a,c),closeGear=overlap(b,c),card=bounds(card)})
