<script setup>
    import { ref, onMounted } from 'vue'
    const apiserv = 'https://0b82-57-129-20-203.ngrok-free.app'

    function getQueryParam(name) {
      const url = new URL(window.location.href)
      return url.searchParams.get(name)
    }
    
    const userId = ref(getQueryParam('user_id') || 1)

    const copySuccess = ref(false)
    const referrals = ref([])

    const referralLink = `${apiserv}/invite?referrer_id=${userId.value}`

    const copyReferralLink = async () => {
    try {
        await navigator.clipboard.writeText(referralLink)
        copySuccess.value = true
        setTimeout(() => {
        copySuccess.value = false
        }, 2000)
    } catch (err) {
        console.error('Failed to copy referral link: ', err)
    }
    }

    const shareReferralLink = () => {
    const message = `🎉 Hello! I invite you to MindGlows. Get bonuses and start earning! 💰\n\n👉 Join us\n5000 coins as a gift\n25000 coins if you have Telegram Premium`

    if (typeof Telegram !== 'undefined' && Telegram.WebApp) {
        Telegram.WebApp.openTelegramLink(
        `https://t.me/share/url?url=${encodeURIComponent(referralLink)}&text=${encodeURIComponent(message)}`
        )
    } else if (navigator.userAgent.includes('Telegram')) {
        window.location.href = `https://t.me/share/url?url=${encodeURIComponent(referralLink)}&text=${encodeURIComponent(message)}`
    } else if (navigator.share) {
        navigator
        .share({
            title: 'Invite to MindGlows',
            text: message,
            url: referralLink,
        })
        .catch((err) => console.error('Ошибка при отправке ссылки:', err))
    } else {
        alert('Telegram WebApp не поддерживается. Отправьте ссылку вручную.')
    }
    }

    const fetchReferrals = async () => {
    try {
        const res = await fetch(`/invited_friends?user_id=${userId.value}`)
        const data = await res.json()
        if (res.ok && data.success) {
        referrals.value = data.referrals
        } else {
        console.error('Failed to load referrals:', data.error)
        }
    } catch (err) {
        console.error('Error fetching referrals:', err)
    }
    }

    onMounted(fetchReferrals)
</script>

<template>
  <div class="container">
    <div id="copy-notification" v-show="copySuccess">Link copied!</div>
    
    <div class="head">
      <h1>Invite your friends!</h1>
      <p>You and your friend will receive bonuses</p>
    </div>

    <div class="new">
      <h3>Invite a friend</h3>
      <p><span style="color:#bd9400">● +5000</span> coins for you and your friend</p>
    </div>

    <div class="new">
      <h3>Invite a friend with Telegram Premium</h3>
      <p><span style="color:#bd9400">● +25000</span> coins for you and your friend</p>
    </div>

    <div class="referals">
      <h2>List of your friends ({{ referrals.length }})</h2>
      <div id="referrals-list">
        <div v-for="ref in referrals" :key="ref.id" class="refblock">
          <img src="/src/assets/user.png" />
          <h3>{{ ref.name }}</h3>
        </div>
      </div>
    </div>

    <div class="invite">
      <button class="inv" @click="shareReferralLink">Invite a friend</button>
      <button class="copy" @click="copyReferralLink">☐</button>
    </div>
  </div>
</template>

<style scoped>
    .container {
        display:block;
        margin:0 auto;
        justify-content: center;
        align-items: center;
        height:78%;
        background: #1e1e1e;
        border-radius: 30px 30px 30px 30px;
        padding: 20px;
        box-shadow: 0px 0px 8px #6366F1;
        text-align: center;
        overflow-y: auto; 
        overflow-x: hidden;
    }

    .head h1{
        margin-top:5px;

    }

    h3{
        margin:0;
        padding:0;
    }

    .new {
        display:block;
        margin:0 auto;
        margin-bottom: 15px;
        padding:15px;
        background: #1e1e1e;
        border-radius: 40px;
        box-shadow: 0px 0px 8px #6366F1;
        justify-content: center;
        align-items: center;
    }

    .referals h2 {
        display:flex;
        font-size:16px;
        margin:0;
        margin-top:50px;
    }


    .refblock {
        display:flex;
        margin:0;
        margin-top: 15px;
        margin-bottom: 15px;
        padding:15px;
        background: #1e1e1e;
        border-radius: 40px;
        box-shadow: 0px 0px 5px #6366F1;
    }

    .refblock img {
        width:25px;
        height:25px;
        padding:5px;
    }

    .refblock h3{
        display:flex;
        margin:0;
        padding:0;
        font-size:15px;
        align-items:center;
    }

    .invite {
        display:flex;
        justify-content:center;
        align-items:center;
        padding-bottom:80px;
    }

    .inv {
        font-size: 25px;
        background-color:#773ffa;
        border: none;
        border-radius:10px;
        padding:10px;
        justify-content:center;
        align-items:center;
        animation: pulse 2s infinite;
        box-shadow: 0 0 12px rgba(139, 92, 246, 0.5);
    }

    .copy {
        display:flex;
        font-size: 25px;
        background-color:#773ffa;
        border: none;
        border-radius:10px;
        padding-top:8px;
        padding-bottom:8px;
        padding-left:15px;
        padding-right:15px;
        justify-content:center;
        align-items:center;
        margin-left:15px;
        box-shadow: 0 0 12px rgba(139, 92, 246, 0.5);

    }
    @keyframes pulse {
        0%, 100% {
            transform: scale(1); 
        }
        50% {
            transform: scale(1.05); 
        }
    }

    #copy-notification {
        display: block;
        position: fixed;
        bottom: 90%;
        left: 50%;
        transform: translateX(-50%);
        background-color: #333333de;
        color: rgb(9, 158, 34);
        padding: 10px;
        border: 2px solid black;
        border-radius: 15px;
        z-index: 1000;
        transition: all 1s;
    }
</style>
