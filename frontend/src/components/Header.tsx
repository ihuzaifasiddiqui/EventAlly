import { Navbar, NavBody, NavItems } from "./ui/resizable-navbar"
import { Contact, HomeIcon, UploadCloud } from "lucide-react"

const Header = () => {
  const navItems = [
    {name: "Home", link: "/", icon: <HomeIcon/>},
    {name: "Upload", link: "/upload", icon: <UploadCloud/>},
    {name: "Contact", link: "/", icon: <Contact/>}
  ]
  return (
    <div>
      <Navbar className="p-4 bg-black border-white">
        <NavBody>
          <NavItems items={navItems} />
        </NavBody>
      </Navbar>
    </div>
  )
}

export default Header