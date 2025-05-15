import { useLocation } from "react-router-dom"
import { Navbar, NavBody, NavItems } from "./ui/resizable-navbar"
import { ChartAreaIcon, Contact, Home, HomeIcon, Network, UploadCloud } from "lucide-react"

const Header = () => {

  const location = useLocation()
  const currentPath = location.pathname
  const isInApp = ["/chat", "/network"].includes(currentPath)

  const navItems = isInApp ? [
    {name: "Chat", link: "/chat", icon: <ChartAreaIcon/>},
    {name: "Network", link: "/network", icon: <Network/>},
  ] : [
    {name: "Home", link: "/", icon: <HomeIcon/>},
    {name: "About", link: "/", icon: <Home/>},
    {name: "Contact", link: "/", icon: <Contact/>}
  ]
  return (
    <div>
      <Navbar className="p-4 bg-black border-white">
        <NavBody>
          <NavItems items={navItems}  />
        </NavBody>
      </Navbar>
    </div>
  )
}

export default Header