import os
import asyncio
import aiofiles # type: ignore
import aiohttp # type: ignore

async def create_recorded_video_post_request_task(session, url, filename, day_record_id):
    filepath = os.path.join('vids', filename)
    payload = aiohttp.FormData()
    async with aiofiles.open(filepath, 'rb') as f:
        file = await f.read()
        payload.add_field('recorded_video', file, filename=filename, content_type='video/avi')
    payload.add_field('day_record_id', day_record_id)
    await session.post(url, data=payload)
    os.remove(filepath)

async def create_current_day_record_get_request_task(session, url):
    response = await session.get(url)
    return await response.json()


def send_recorded_videos(session, url, filenames, day_record_id):
    tasks = []
    for filename in filenames:
        tasks.append(asyncio.create_task(create_recorded_video_post_request_task(session, url, filename, day_record_id)))
    return tasks


def send_profile_user_image(session, url, user_data):
    payload = {
        'profileImage': user_data[0],
        'name': user_data[1],
    }
    return asyncio.create_task(session.post(url, data=payload))



if __name__ == '__main__':
    async def main():
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(*send_recorded_videos(session, 'http://192.168.1.2:8500/api/v1/detections', os.listdir('vids'), '663b6df08c093ab36dd1f5f9'))
    asyncio.run(main())
