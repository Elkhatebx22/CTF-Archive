<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        $adminPassword = config('catdesk.admin_password');

        if (! is_string($adminPassword) || $adminPassword === '') {
            $adminPassword = bin2hex(random_bytes(32));
        }

        User::updateOrCreate([
            'username' => config('catdesk.admin_username'),
        ], [
            'display_name' => 'Site Administrator',
            'bio' => 'Maintains the CatDesk team workspace.',
            'password' => Hash::make($adminPassword),
            'is_admin' => true,
        ]);
    }
}
