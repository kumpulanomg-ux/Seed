import asyncio
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message
)
from pyrogram.enums import GiftForResaleOrder, GiftAttributeType
from typing import List, Dict, Optional, Set
import logging
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

# تحميل ملف gift.env
load_dotenv("gift.env")

class Config:
    IDS = [
        5782984811920491178, 5773668482394620318, 6005659564635063386,
        5933793770951673155, 5897593557492957738, 5868348541058942091,
        5868220813026526561, 5868503709637411929, 5868659926187901653,
        6028426950047957932, 6023752243218481939, 6003373314888696650,
        6001538689543439169, 6003643167683903930, 6001473264306619020,
        5983484377902875708, 5983259145522906006, 5983471780763796287,
        5981132629905245483, 5980789805615678057, 5981026247860290310,
        5933590374185435592, 5936017773737018241, 5935936766358847989,
        5936043693864651359, 5936085638515261992, 5933531623327795414,
        5933629604416717361, 5933671725160989227, 5913442287462908725,
        5915502858152706668, 5915733223018594841, 5915521180483191380,
        5915550639663874519, 5913517067138499193, 5879737836550226478,
        5882125812596999035, 5882252952218894938, 5857140566201991735,
        5856973938650776169, 5846226946928673709, 5846192273657692751,
        5845776576658015084, 5825895989088617224, 5825801628657124140,
        5825480571261813595, 5843762284240831056, 5841689550203650524,
        5841632504448025405, 5841391256135008713, 5839038009193792264,
        5841336413697606412, 5837063436634161765, 5836780359634649414,
        5837059369300132790, 5821384757304362229, 5821205665758053411,
        5821261908354794038, 5170594532177215681, 5167939598143193218,
        5783075783622787539, 5782988952268964995,
        
        6012345678901234567, 6012345678901234568, 6012345678901234569,
        6012345678901234570, 6012345678901234571, 6012345678901234572,
        6012345678901234573, 6012345678901234574, 6012345678901234575,
        6012345678901234576, 6012345678901234577, 6012345678901234578,
        6012345678901234579, 6012345678901234580, 6012345678901234581,
        6012345678901234582, 6012345678901234583, 6012345678901234584,
        6012345678901234585, 6012345678901234586, 6012345678901234587,
        6012345678901234588, 6012345678901234589, 6012345678901234590,
        6012345678901234591, 6012345678901234592, 6012345678901234593,
        6012345678901234594, 6012345678901234595, 6012345678901234596,
        6012345678901234597, 6012345678901234598, 6012345678901234599,
        6012345678901234600, 6012345678901234601, 6012345678901234602,
        6012345678901234603, 6012345678901234604, 6012345678901234605,
        6012345678901234606, 6012345678901234607, 6012345678901234608,
        6012345678901234609, 6012345678901234610, 6012345678901234611,
        6012345678901234612, 6012345678901234613, 6012345678901234614,
        6012345678901234615, 6012345678901234616, 6012345678901234617,
        6012345678901234618, 6012345678901234619, 6012345678901234620,
        6012345678901234621, 6012345678901234622, 6012345678901234623,
        6012345678901234624, 6012345678901234625, 6012345678901234626,
        6012345678901234627, 6012345678901234628, 6012345678901234629,
        6012345678901234630, 6012345678901234631, 6012345678901234632,
        6012345678901234633, 6012345678901234634, 6012345678901234635,
        6012345678901234636, 6012345678901234637, 6012345678901234638,
        6012345678901234639, 6012345678901234640, 6012345678901234641,
        6012345678901234642, 6012345678901234643, 6012345678901234644,
        6012345678901234645, 6012345678901234646, 6012345678901234647,
        6012345678901234648, 6012345678901234649, 6012345678901234650
    ]
    
    RULES = {
        5170594532177215681: 150, 
        5782988952268964995: 150, 
        6028426950047957932: 175, 
        5782984811920491178: 175,
    }
    
    
    PRICE = 300
    CHANEL = -1002844864478
    INTERVAL = 1
    CHECK = 10
    CHECKS = 30

    # القيم الحساسة من gift.env
    FR3ON = os.getenv("SESSION_STRING")
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")


class GiftBot:
    def __init__(self, client: Client):
        self.client = client
        self.posted_gifts: Set[str] = set()
        self.logger = self.setup_logger()
        self.last_check = datetime.now()
        self.semaphore = asyncio.Semaphore(Config.CHECKS)
        self.user_client = None 
    
    def setup_logger(self):
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        return logging.getLogger(__name__)
    
    def get_max_price(self, gift_id: int) -> int:
        return Config.RULES.get(gift_id, Config.PRICE)
    
    async def initialize_user_client(self):
        self.user_client = Client(
            name="user_account",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
        )
        await self.user_client.start()
        self.logger.info("User client initialized for gift checking")
    
    async def search_affordable_gifts(self, gift_id: int) -> List[Dict]:
        max_price = self.get_max_price(gift_id)
        
        try:
            async with self.semaphore:
                gifts = []
                async for gift in self.user_client.search_gifts_for_resale(
                    gift_id=gift_id,
                    order=GiftForResaleOrder.PRICE,
                    limit=50 
                ):
                    if (gift.last_resale_price and 
                        gift.last_resale_price <= max_price and
                        gift.link not in self.posted_gifts):
                        gifts.append(gift)
                        if len(gifts) >= Config.CHECK * 3:  
                            break
                return gifts
        except Exception as e:
            self.logger.error(f"Error searching gifts {gift_id}: {e}")
            return []

    def format_gift_details(self, gift) -> str:
        attributes = []
        for attr in gift.attributes:
            attr_type = ""
            if attr.type == GiftAttributeType.MODEL:
                attr_type = "🖼️ Model"
            elif attr.type == GiftAttributeType.BACKDROP:
                attr_type = "🎨 Backdrop"
            elif attr.type == GiftAttributeType.SYMBOL:
                attr_type = "✨ Symbol"
            
            if attr_type:
                attributes.append(
                    f"{attr_type}: {attr.name} ({attr.rarity/10}% rare)"
                )

        owner = f"@{gift.owner.username}" if gift.owner and gift.owner.username else "Private Seller"
        
        price_status = ""
        if gift.last_resale_price <= 175:
            price_status = "💎 BEST PRICE! 💎"
        elif gift.last_resale_price <= 200:
            price_status = "💰 GOOD PRICE!"
        else:
            price_status = "💵 FAIR PRICE"
        
        random_emoji = random.choice(["🎁", "🎀", "🎊", "🎉", "🛍️", "💝"])
        
        return (
            f"{random_emoji} **{gift.title}** {random_emoji}\n\n"
            f"👤 **Seller:** {owner}\n"
            f"💰 **Price:** {gift.last_resale_price} stars ({price_status})\n"
            f"📦 **Stock:** {gift.number:,}/{gift.total_amount:,}\n\n"
            f"{chr(10).join(attributes) if attributes else '📌 No special attributes'}\n\n"
            f"🔗 [View Gift Details]({gift.link})"
        )

    def create_action_button(self, gift_link: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Buy Gift Now", url=gift_link)]
        ])

    async def send_gift_alert(self, gift) -> Optional[Message]:
        try:
            message = self.format_gift_details(gift)
            keyboard = self.create_action_button(gift.link)
            
            sent_message = await self.client.send_message(
                chat_id=Config.CHANEL,
                text=message,
                reply_markup=keyboard,
                disable_web_page_preview=False
            )
            
            self.posted_gifts.add(gift.link)
            self.logger.info(f"Posted gift: {gift.title} | Price: {gift.last_resale_price}")
            return sent_message
        except Exception as e:
            self.logger.error(f"Failed to send gift: {e}")
            return None

    async def check_gift_type(self, gift_id: int):
        gifts = await self.search_affordable_gifts(gift_id)
        sent_count = 0
        for gift in gifts[:Config.CHECK]:
            if sent_count >= Config.CHECK:
                break
            await self.send_gift_alert(gift)
            sent_count += 1
            await asyncio.sleep(1)  
        return sent_count

    async def monitor_gifts(self):
        self.logger.info("Starting Gift Monitor...")
        self.logger.info(f"Tracking {len(Config.IDS)} gift types")
        
        await self.initialize_user_client()
        
        while True:
            try:
                self.last_check = datetime.now()
                total_found = 0
    
                shuffled_ids = Config.IDS.copy()
                random.shuffle(shuffled_ids)
                
                chunk_size = Config.CHECKS
                for i in range(0, len(shuffled_ids), chunk_size):
                    chunk = shuffled_ids[i:i + chunk_size]
                    tasks = [self.check_gift_type(gift_id) for gift_id in chunk]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for result in results:
                        if isinstance(result, int):
                            total_found += result
                    
                    await asyncio.sleep(1)
                
                status_msg = (
                    f"Cycle complete. Found {total_found} gifts. "
                    f"Next check in {Config.INTERVAL} seconds..."
                )
                self.logger.info(status_msg)
                
                await asyncio.sleep(Config.INTERVAL)
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(1)  

async def run_bot():
    bot_client = Client(
        name="user_session",             # اسم قصير عادي
        session_string=Config.FR3ON,     # السيشن سترنج الطويل
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        sleep_threshold=60,
        workers=900,
        max_concurrent_transmissions=30
    )

    async with bot_client:
        bot = GiftBot(bot_client)
        await bot.monitor_gifts()





if __name__ == "__main__":
    print("Starting Telegram Gift Bot...")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(run_bot())
    except KeyboardInterrupt:
        print("\nتم تشغيل البوت يافرعون✅")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        loop.close()