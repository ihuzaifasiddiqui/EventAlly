import { Navbar, NavBody, NavItems } from "./ui/resizable-navbar"
import { ChartAreaIcon, Contact, HomeIcon, UploadCloud } from "lucide-react"

const Header = () => {
  const navItems = [
    {name: "Home", link: "/", icon: <HomeIcon/>},
    {name: "Upload", link: "/upload", icon: <UploadCloud/>},
    {name: "Chat", link: "/chat", icon: <ChartAreaIcon/>},
    {name: "Contact", link: "/", icon: <Contact/>}
  ]
  return (
    <div>
    <Navbar className="p-4 border-white">
      <NavBody>
        <NavItems items={navItems} />
      </NavBody>
    </Navbar>
    </div>
  )
}

export default Header