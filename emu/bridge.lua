local D=""
local seq=0
local stick=nil local hold={} local holdn=0 local waitn=0 local pending=nil
local function split(s) local t={} for w in s:gmatch("%S+") do t[#t+1]=w end return t end
local function ack(msg) local f=io.open(D.."ack.tmp","w") f:write(msg) f:close() os.remove(D.."ack.txt") os.rename(D.."ack.tmp",D.."ack.txt") end
local queue={}
local function readcmd()
  local f=io.open(D.."cmd.txt","r") if not f then return end
  local s=f:read("*a") f:close() os.remove(D.."cmd.txt")
  for line in s:gmatch("[^\n]+") do queue[#queue+1]=line end
end
local function step()
  if holdn>0 or waitn>0 then return end
  while #queue>0 do
    local line=table.remove(queue,1) local a=split(line) local c=a[1]
    if c=="hold" then hold={} for b in a[2]:gmatch("[^,]+") do hold["P1 "..b:gsub("_"," ")]=true end holdn=tonumber(a[3]) return
    elseif c=="wait" then waitn=tonumber(a[2]) return
    elseif c=="shot" then client.screenshot(a[2])
    elseif c=="save" then savestate.save(a[2])
    elseif c=="load" then savestate.load(a[2])
    elseif c=="dump" then
      local addr=tonumber(a[2]) local n=tonumber(a[3]) local t=memory.read_bytes_as_array(addr,n,"RDRAM")
      local f=io.open(a[4],"wb") local parts={} for i=1,#t do parts[#parts+1]=string.char(t[i]) end f:write(table.concat(parts)) f:close()
    elseif c=="wfile" then
      local f=io.open(a[3],"rb") local d=f:read("*a") f:close() local base=tonumber(a[2])
      for i=1,#d do memory.writebyte(base+i-1,d:byte(i),"RDRAM") end
    elseif c=="w8" then memory.writebyte(tonumber(a[2]),tonumber(a[3]),"RDRAM")
    elseif c=="watch" then
      local addr=tonumber(a[2]) local lf=io.open(a[3],"w")
      local cnt=0
      event.onmemoryread(function(ad,v,fl)
        if cnt<40 then cnt=cnt+1 local r=emu.getregisters() local t={} 
          for k,x in pairs(r) do t[#t+1]=k.."="..string.format("%x",x) end
          table.sort(t) lf:write(string.format("%x ",ad)..table.concat(t," ")..string.char(10)) lf:flush() end
      end, addr, "System Bus")
    elseif c=="unwatch" then event.unregisterbyname("") 
    elseif c=="xwatch" then
      local lf=io.open(a[3],"w")
      local kk=0
      event.onmemoryexecute(function()
          local r=emu.getregisters()
          if kk==0 then kk=1 local t={} for k,x in pairs(r) do t[#t+1]=k end table.sort(t) lf:write(table.concat(t," ")..string.char(10)) end
lf:write(string.format("F%d PC %x a0=%x a1=%x a2=%x a3=%x ra=%x v1=%x t0=%x t9=%x",emu.framecount(),r["PC"] or 0,r["a0_lo"] or 0,r["a1_lo"] or 0,r["a2_lo"] or 0,r["a3_lo"] or 0,r["ra_lo"] or 0,r["v1_lo"] or 0,r["t0_lo"] or 0,r["t9_lo"] or 0)..string.char(10)) lf:flush()
      end, tonumber(a[2]), "System Bus")
    elseif c=="wwatch" then
      local lf=io.open(a[3],"w") local cnt=0
      event.onmemorywrite(function(ad,v,fl)
          if cnt<30 then cnt=cnt+1 local r=emu.getregisters() local t={} for i=1,31 do t[#t+1]=string.format("r%d=%x",i,r["REG"..i] or 0) end lf:write(string.format("%x v=%x PC %x ",ad,v or 0,r["PC"] or 0)..table.concat(t," ")..string.char(10)) lf:flush() end
      end, tonumber(a[2]), a[4] or "System Bus")
    elseif c=="stick" then stick={["P1 X Axis"]=tonumber(a[2]),["P1 Y Axis"]=tonumber(a[3])} holdn=tonumber(a[4]) hold={} if a[5] then for b in a[5]:gmatch("[^,]+") do hold["P1 "..b:gsub("_"," ")]=true end end return
    elseif c=="reboot" then client.reboot_core()
    elseif c=="ack" then ack(a[2])
    elseif c=="quit" then client.exit()
    end
  end
end
while true do
  readcmd() step()
  if holdn>0 then joypad.set(hold) if stick then joypad.setanalog(stick) end holdn=holdn-1 if holdn==0 and stick then joypad.setanalog({["P1 X Axis"]="",["P1 Y Axis"]=""}) stick=nil end end
  if waitn>0 then waitn=waitn-1 end
  emu.frameadvance()
end
