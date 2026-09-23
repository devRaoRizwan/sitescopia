import { FallbackIcon, ICONS } from './socialIcons'



export default function SocialMark({ platform }) {
  const Icon = ICONS[platform] ?? FallbackIcon
  return <Icon className="social-icon" />
}
