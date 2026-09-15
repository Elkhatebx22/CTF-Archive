<?php

use App\Http\Controllers\AccountController;
use App\Http\Controllers\AdminController;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\NoteController;
use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('home');
})->name('home');

Route::middleware('guest')->group(function (): void {
    Route::get('/register', [AuthController::class, 'registerForm'])->name('register');
    Route::post('/register', [AuthController::class, 'register']);
    Route::get('/login', [AuthController::class, 'loginForm'])->name('login');
    Route::post('/login', [AuthController::class, 'login']);
});

Route::middleware('auth')->group(function (): void {
    Route::post('/logout', [AuthController::class, 'logout'])->name('logout');
    Route::get('/dashboard', DashboardController::class)->name('dashboard');

    Route::get('/account/profile', [AccountController::class, 'profile'])
        ->name('account.profile');
    Route::post('/account/profile', [AccountController::class, 'updateProfile'])
        ->name('account.profile.update');
    Route::patch('/account/profile', [AccountController::class, 'updateProfile']);
    Route::get('/account/password', [AccountController::class, 'passwordForm'])
        ->name('account.password');
    Route::post('/account/password', [AccountController::class, 'updatePassword'])
        ->name('account.password.update');
    Route::patch('/account/password', [AccountController::class, 'updatePassword']);

    Route::post('/notes', [NoteController::class, 'store'])->name('notes.store');
    Route::get('/notes/{note}/edit', [NoteController::class, 'edit'])->name('notes.edit');
    Route::post('/notes/{note}', [NoteController::class, 'update'])->name('notes.update');
    Route::patch('/notes/{note}', [NoteController::class, 'update']);
    Route::post('/notes/{note}/delete', [NoteController::class, 'destroy'])->name('notes.destroy');
    Route::delete('/notes/{note}', [NoteController::class, 'destroy']);

    Route::get('/admin', AdminController::class)->name('admin');
    Route::get('/admin/flag', [AdminController::class, 'flag'])->name('admin.flag');
});
